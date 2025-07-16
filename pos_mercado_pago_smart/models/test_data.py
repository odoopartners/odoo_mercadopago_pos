create_order_data_resp = {
    "id": "ORD00001111222233334444555566",
    "type": "point",
    "user_id": "5238400195",
    "external_reference": "ext_ref_1234",
    "description": "Smartphone",
    "processing_mode": "automatic",
    "country_code": "CHL",
    "integration_data": {
        "application_id": "1234567890",
        "platform_id": "dev_1234567890",
        "integrator_id": "dev_123456",
        "sponsor": {
            "id": "446566691"
        }
    },
    "status": "created",
    "status_detail": "created",
    "created_date": "2024-09-10T14:26:42.109320977Z",
    "last_updated_date": "2024-09-10T14:26:42.109320977Z",
    "config": {
        "point": {
            "terminal_id": "PAX_N950__SMARTPOS1423",
            "print_on_terminal": "no_ticket",
            "ticket_number": "S0392JED"
        },
        "payment_method": {
            "default_type": "credit_card",
            "default_installments": "6"
        }
    },
    "transactions": {
        "payments": [
            {
                "id": "PAY01J67CQQH5904WDBVZEM4JMEP3",
                "amount": "24",
                "status": "created"
            }
        ]
    },
    "taxes": [
        {
            "payer_condition": "payment_taxable_iva"
        }
    ]
}

get_order_data_resp = {
    "id": "ORD00001111222233334444555566",
    "user_id": "5238400195",
    "type": "point",
    "external_reference": "ext_ref_1234",
    "processing_mode": "automatic",
    "description": "Smartphone",
    "country_code": "CHL",
    "integration_data": {
        "application_id": "1234567890",
        "platform_id": "dev_1234567890",
        "integrator_id": "dev_123456",
        "sponsor": {
            "id": "446566691"
        }
    },
    # "status": "refunded",
    "status": "finished",
    "status_detail": "refunded",
    "created_date": "2024-09-10T14:26:42.109320977Z",
    "last_updated_date": "2024-09-10T14:26:42.109320977Z",
    "config": {
        "point": {
            "terminal_id": "PAX_N950__SMARTPOS1423",
            "print_on_terminal": "no_ticket",
            "ticket_number": "S0392JED"
        },
        "payment_method": {
            "default_type": "credit_card",
            "default_installments": "6"
        }
    },
    "transactions": {
        "payments": [
            {
                "id": "PAY01J67CQQH5904WDBVZEM4JMEP3",
                "amount": "24",
                "refunded_amount": "38",
                "tip_amount": "14",
                "paid_amount": "38",
                "status": "refunded",
                "status_detail": "created",
                "reference_id": "12345678",
                "payment_method": {
                    "type": "credit_card",
                    "installments": 1,
                    "id": "master"
                }
            }
        ],
        "refunds": [
            {
                "id": "REF01J67CQQH5904WDBVZEM1234D",
                "transaction_id": "PAY01J67CQQH5904WDBVZEM4JMEP3",
                "reference_id": "12345678",
                "amount": "38",
                "status": "processed"
            }
        ]
    },
    "taxes": [
        {
            "payer_condition": "payment_taxable_iva"
        }
    ]
}

refund_data_resp = {
  "id": "ORD0000ABCD222233334444555566",
  "status": "refunded",
  "status_detail": "refunded",
  "transactions": {
    "refunds": [
      {
        "id": "REF01J67CQQH5904WDBVZEM1234D",
        "transaction_id": "PAY01J67CQQH5904WDBVZEM4JMEP3",
        "reference_id": "12345678",
        "amount": "38",
        "status": "processed"
      }
    ]
  }
}
