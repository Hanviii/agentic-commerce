import os

import razorpay
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

router = APIRouter(prefix="/payment", tags=["Payment"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    print("WARNING: Razorpay keys are not configured.")

client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET,
    )
)


class CreateOrderRequest(BaseModel):
    amount: float


@router.post("/create-order")
def create_order(request: CreateOrderRequest):

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero."
        )

    try:
        # Razorpay expects amount in paise
        amount_in_paise = int(request.amount * 100)

        order = client.order.create(
            {
                "amount": amount_in_paise,
                "currency": "INR",
                "payment_capture": 1,
            }
        )

        return {
            "order_id": order["id"],
            "amount": request.amount,
            "currency": "INR",
            "key_id": RAZORPAY_KEY_ID,
        }

    except Exception as e:
        print("RAZORPAY ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Unable to create payment order."
        )