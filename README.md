# Agentic Commerce

> AI-powered product discovery and checkout automation using natural language.

## Overview

Agentic Commerce is an AI-powered shopping assistant that allows users to describe what they want to buy using natural language instead of manually browsing through filters.

The system understands the user's requirements, converts them into structured shopping intent, searches a product knowledge graph, ranks suitable products, and guides the user towards checkout.

The goal is to move e-commerce from:

**Search → Filter → Compare → Checkout**

towards:

**Tell the agent what you want → Let the agent do the work**

---

## Problem

Traditional e-commerce requires users to manually:

- Search for products
- Apply multiple filters
- Compare ratings and specifications
- Identify the best matching product
- Navigate through checkout
- Select a suitable payment method

This becomes inefficient when a user has multiple constraints.

For example:

> "Buy me wireless earbuds under ₹3000 with above 4 star rating and active noise cancellation via Navi UPI."

The user should not have to manually translate this request into several filters.

---

## Solution

Agentic Commerce understands the complete request and extracts structured intent such as:

- Product category
- Price constraints
- Minimum rating
- Required features
- Payment preference

The extracted intent is then used to query the product database and return relevant products with AI-generated recommendations.

---

## Example

### User Request

> Buy me wireless earbuds under ₹3000 with above 4 star rating and active noise cancellation via Navi UPI.

### AI-Extracted Intent

```json
{
  "category": "Earbuds",
  "max_price": 3000,
  "min_rating": 4,
  "noise_cancellation": true,
  "wireless": true,
  "payment_method": "Navi UPI"
}
