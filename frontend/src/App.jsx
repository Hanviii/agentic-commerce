import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [cart, setCart] = useState([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState("");

  // =========================
  // SEARCH
  // =========================

  const searchProducts = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchQuery,
        }),
      });

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const data = await response.json();

console.log("BACKEND RESPONSE:", data);
console.log("PRODUCT COUNT:", data.count);
console.log("PRODUCTS:", data.products);
console.log("PAYMENT:", data.intent?.payment_method);

setResults(data);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // SUGGESTIONS
  // =========================

  const handleSuggestion = (text) => {
    setQuery(text);
    searchProducts(text);
  };

  // =========================
  // CART
  // =========================

  const addToCart = (product) => {
    setPaymentStatus("");

    setCart((currentCart) => {
      const existing = currentCart.find(
        (item) => item.id === product.id
      );

      if (existing) {
        return currentCart.map((item) =>
          item.id === product.id
            ? {
                ...item,
                quantity: item.quantity + 1,
              }
            : item
        );
      }

      return [
        ...currentCart,
        {
          ...product,
          quantity: 1,
        },
      ];
    });

    setCartOpen(true);
  };

  const increaseQuantity = (productId) => {
    setCart((currentCart) =>
      currentCart.map((item) =>
        item.id === productId
          ? {
              ...item,
              quantity: item.quantity + 1,
            }
          : item
      )
    );
  };

  const decreaseQuantity = (productId) => {
    setCart((currentCart) =>
      currentCart
        .map((item) =>
          item.id === productId
            ? {
                ...item,
                quantity: item.quantity - 1,
              }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  };

  const cartTotal = cart.reduce(
    (total, item) =>
      total + item.price * item.quantity,
    0
  );

  const cartItemCount = cart.reduce(
    (total, item) =>
      total + item.quantity,
    0
  );

  // =========================
  // RAZORPAY CHECKOUT
  // =========================

  const handleCheckout = async () => {
    if (cart.length === 0) {
      alert("Your cart is empty.");
      return;
    }

    setPaymentStatus("");

    try {
      console.log(
        "Creating Razorpay order:",
        cartTotal
      );

      const response = await fetch(
        `${API_URL}/payment/create-order`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            amount: cartTotal,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to create payment order"
        );
      }

      const order = await response.json();

      console.log(
        "Razorpay order:",
        order
      );

      if (!window.Razorpay) {
        throw new Error(
          "Razorpay Checkout script not loaded"
        );
      }

      // Detect user's requested payment method.
      const paymentMethod =
        results?.intent?.payment_method || "";

      const isUPI =
        paymentMethod
          .toLowerCase()
          .includes("upi");

      const options = {
        key: order.key_id,

        amount: Math.round(
          cartTotal * 100
        ),

        currency:
          order.currency || "INR",

        name: "Agentic Commerce",

        description:
          "AI-powered product purchase",

        order_id:
          order.order_id,

        handler: function (response) {
          console.log(
            "PAYMENT SUCCESS:",
            response
          );

          alert(
            `Payment successful!\n\nPayment ID: ${response.razorpay_payment_id}`
          );

          // Clear cart only after successful payment.
          setCart([]);
          setCartOpen(false);
          setPaymentStatus("");
        },

        prefill: {
          name: "Demo User",
          email: "demo@example.com",
          contact: "9999999999",

          // If user requested UPI,
          // pre-select UPI in Razorpay.
          ...(isUPI
            ? {
                method: "upi",
              }
            : {}),
        },

        theme: {
          color: "#111111",
        },

        modal: {
          ondismiss: function () {
            console.log(
              "Payment popup closed"
            );

            // Keep cart intact.
            setPaymentStatus(
              "Payment cancelled. Your cart is still saved."
            );

            setCartOpen(true);
          },
        },
      };

      const razorpay =
        new window.Razorpay(options);

      razorpay.on(
        "payment.failed",
        function (response) {
          console.error(
            "PAYMENT FAILED:",
            response.error
          );

          setPaymentStatus(
            "Payment failed. Your cart is still saved."
          );

          setCartOpen(true);

          alert(
            `Payment failed:\n${response.error.description}`
          );
        }
      );

      razorpay.open();

    } catch (error) {
      console.error(
        "CHECKOUT ERROR:",
        error
      );

      setPaymentStatus(
        "Unable to start checkout. Your cart is still saved."
      );

      setCartOpen(true);

      alert(
        "Unable to start checkout. Please make sure the backend is running."
      );
    }
  };

  // =========================
  // UI
  // =========================

  return (
    <div className="app">

      {/* ================= HEADER ================= */}

      <header className="header">

        <div className="brand">

          <div className="logo">
            A
          </div>

          <span>
            Agentic Commerce
          </span>

        </div>


        <div className="header-actions">

          <div className="tagline">
            AI-Powered Product Discovery
          </div>

          <button
            className="cart-button"
            onClick={() => {
              setPaymentStatus("");
              setCartOpen(true);
            }}
          >
            🛒 Cart ({cartItemCount})
          </button>

        </div>

      </header>


      {/* ================= CART ================= */}

      {cartOpen && (

        <div className="cart-overlay">

          <div className="cart-panel">

            <div className="cart-header">

              <h2>
                Your Cart
              </h2>

              <button
                onClick={() =>
                  setCartOpen(false)
                }
              >
                ✕
              </button>

            </div>


            {/* PAYMENT STATUS */}

            {paymentStatus && (

              <div className="payment-status">
                {paymentStatus}
              </div>

            )}


            {/* EMPTY CART */}

            {cart.length === 0 ? (

              <div className="empty-cart">

                <p>
                  Your cart is empty.
                </p>

                <button
                  className="continue-shopping"
                  onClick={() =>
                    setCartOpen(false)
                  }
                >
                  Continue Shopping
                </button>

              </div>

            ) : (

              <>
                {/* CART ITEMS */}

                <div className="cart-items">

                  {cart.map((item) => (

                    <div
                      className="cart-item"
                      key={item.id}
                    >

                      <div>

                        <strong>
                          {item.name}
                        </strong>

                        <p>
                          ₹
                          {item.price.toLocaleString(
                            "en-IN"
                          )}
                        </p>

                      </div>


                      <div className="quantity-controls">

                        <button
                          onClick={() =>
                            decreaseQuantity(
                              item.id
                            )
                          }
                        >
                          −
                        </button>

                        <span>
                          {item.quantity}
                        </span>

                        <button
                          onClick={() =>
                            increaseQuantity(
                              item.id
                            )
                          }
                        >
                          +
                        </button>

                      </div>

                    </div>

                  ))}

                </div>


                {/* CART TOTAL */}

                <div className="cart-total">

                  {/* PAYMENT PREFERENCE */}

                  {results?.intent?.payment_method && (

                    <div className="payment-preference">

                      ✦ Payment preference detected:{" "}

                      <strong>
                        {
                          results.intent
                            .payment_method
                        }
                      </strong>

                    </div>

                  )}


                  <strong>
                    Total: ₹
                    {cartTotal.toLocaleString(
                      "en-IN"
                    )}
                  </strong>


                  <button
                    className="checkout-button"
                    onClick={
                      handleCheckout
                    }
                  >
                    Proceed to Checkout
                  </button>


                  <button
                    className="continue-shopping"
                    onClick={() =>
                      setCartOpen(false)
                    }
                  >
                    Continue Shopping
                  </button>

                </div>

              </>

            )}

          </div>

        </div>

      )}


      {/* ================= HERO ================= */}

      {!results && (

        <main className="hero">

          <div className="badge">
            ✦ &nbsp; INTELLIGENT SHOPPING
          </div>


          <h1>

            <span>
              Tell us what you want.
            </span>

            <strong>
              We'll find it.
            </strong>

          </h1>


          <p className="subtitle">

            Search naturally. Our AI understands
            your requirements, finds matching
            products, and recommends the best
            options.

          </p>


          <SearchBox
            query={query}
            setQuery={setQuery}
            onSearch={() =>
              searchProducts()
            }
            loading={loading}
          />


          <div className="try-section">

            <span>
              Try:
            </span>


            <button
              onClick={() =>
                handleSuggestion(
                  "Smartwatch with GPS"
                )
              }
            >
              Smartwatch + GPS
            </button>


            <button
              onClick={() =>
                handleSuggestion(
                  "Mechanical keyboard with RGB"
                )
              }
            >
              Mechanical keyboard + RGB
            </button>


            <button
              onClick={() =>
                handleSuggestion(
                  "Earbuds with ANC"
                )
              }
            >
              Earbuds + ANC
            </button>

          </div>

        </main>

      )}


      {/* ================= RESULTS ================= */}

      {results && (

        <main className="results-page">

          <div className="results-search">

            <SearchBox
              query={query}
              setQuery={setQuery}
              onSearch={() =>
                searchProducts()
              }
              loading={loading}
            />

          </div>


          <div className="results-header">

            <div>

              <p className="eyebrow">
                SEARCH RESULTS
              </p>

              <h2>
                Products matching your needs
              </h2>

              <p>
                {results.count} products found
              </p>

            </div>


            <button
              className="new-search"
              onClick={() =>
                setResults(null)
              }
            >
              New search
            </button>

          </div>


          {/* AI RECOMMENDATION */}

          {results.recommendations && (

            <section className="recommendation">

              <div className="recommendation-icon">
                ✦
              </div>

              <div>

                <div className="recommendation-label">
                  AI RECOMMENDATION
                </div>

                <p>
                  {
                    results
                      .recommendations
                      .summary
                  }
                </p>

              </div>

            </section>

          )}


          {/* PRODUCTS */}

          <section className="products-grid">

            {results.products.map(
              (product) => (

                <ProductCard
                  key={product.id}
                  product={product}
                  recommendations={
                    results
                      .recommendations
                      ?.recommendations || []
                  }
                  onAddToCart={
                    addToCart
                  }
                />

              )
            )}

          </section>

        </main>

      )}


      {/* ERROR */}

      {error && (

        <div className="error">
          {error}
        </div>

      )}

    </div>
  );
}


// ==================================================
// SEARCH BOX
// ==================================================

function SearchBox({
  query,
  setQuery,
  onSearch,
  loading,
}) {

  return (

    <div className="search-container">

      <input
        value={query}
        onChange={(e) =>
          setQuery(e.target.value)
        }
        onKeyDown={(e) => {

          if (e.key === "Enter") {
            onSearch();
          }

        }}
        placeholder="Describe what you're looking for..."
      />


      <button
        onClick={onSearch}
        disabled={loading}
      >
        {loading
          ? "Searching..."
          : "Search"}
      </button>

    </div>

  );
}


// ==================================================
// PRODUCT CARD
// ==================================================

function ProductCard({
  product,
  recommendations,
  onAddToCart,
}) {

  const recommendation =
    recommendations.find(
      (item) =>
        item.product_id === product.id
    );


  return (

    <article className="product-card">

      <div className="product-top">

        <div className="product-placeholder">

          {product.category ===
          "Smartwatch"

            ? "⌚"

            : product.category ===
              "Earbuds"

            ? "🎧"

            : "⌨️"}

        </div>


        {recommendation && (

          <div className="recommended">
            ✦ Recommended
          </div>

        )}

      </div>


      <div className="product-content">

        <div className="brand-name">
          {product.brand}
        </div>


        <h3>
          {product.name}
        </h3>


        <div className="rating">
          ★ {product.rating}
        </div>


        <div className="price">
          ₹
          {product.price.toLocaleString(
            "en-IN"
          )}
        </div>


        <div className="features">

          {product.battery_days && (

            <span>
              🔋 {product.battery_days} days
            </span>

          )}


          {product.battery_hours && (

            <span>
              🔋 {product.battery_hours} hrs
            </span>

          )}


          {product.gps && (
            <span>GPS</span>
          )}


          {product.calling && (
            <span>Calling</span>
          )}


          {product.noise_cancellation && (
            <span>ANC</span>
          )}


          {product.spatial_audio && (

            <span>
              Spatial Audio
            </span>

          )}


          {product.rgb && (
            <span>RGB</span>
          )}


          {product.wireless && (

            <span>
              Wireless
            </span>

          )}

        </div>


        {recommendation && (

          <div className="reason">
            {recommendation.reason}
          </div>

        )}


        <button
          className="buy-button"
          onClick={() =>
            onAddToCart(product)
          }
        >
          Add to Cart
        </button>

      </div>

    </article>

  );
}


export default App;