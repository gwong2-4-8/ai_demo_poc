-- Insert 1 inactive draft SKU with an inverted ERP price feed (unit_price_usd < unit_cost_usd)
-- to empirically trigger the Knowledge Catalog Auto Data Quality Margin Floor Guardrail rule
-- without affecting fulfilled Net Recognized Revenue ($1,452,445.56).

INSERT INTO public.products (sku, product_name, vendor, category, unit_cost_usd, unit_price_usd, active)
VALUES ('IM-OEM-ERR99', 'Draft Server Bundle - Inverted ERP Price Feed', 'GenericOEM', 'Enterprise Servers', 4200.00, 3850.00, FALSE)
ON CONFLICT (sku) DO UPDATE
SET unit_cost_usd = EXCLUDED.unit_cost_usd,
    unit_price_usd = EXCLUDED.unit_price_usd,
    active = EXCLUDED.active,
    updated_at = NOW();
