UPDATE pos_payment_method
   SET mp_client_id = '-',
       mp_client_secret = '-',
       mp_refresh_token = '-',
       mp_pkce = '-',
       mp_pkce_code_verifier = '-',
       mp_bearer_token = null,
       mp_token_lifetime = null;
