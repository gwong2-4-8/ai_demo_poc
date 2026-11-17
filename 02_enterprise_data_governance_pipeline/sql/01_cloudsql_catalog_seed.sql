-- Ingram Micro B2B Computer Catalog & Product Transactions Schema (Cloud SQL for PostgreSQL)
-- Target Instance: demo1-371900:us-west1:ingram-catalog-sql | Database: ingram_catalog

DROP TABLE IF EXISTS public.product_transactions CASCADE;
DROP TABLE IF EXISTS public.products CASCADE;

CREATE TABLE public.products (
    sku VARCHAR(32) PRIMARY KEY,
    product_name VARCHAR(128) NOT NULL,
    vendor VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    unit_cost_usd NUMERIC(10, 2) NOT NULL,
    unit_price_usd NUMERIC(10, 2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.products IS 'Ingram Micro master B2B computer hardware and enterprise IT catalog with SKU list prices and distributor unit costs.';
COMMENT ON COLUMN public.products.sku IS 'Globally unique Ingram Micro Stock Keeping Unit identifier (IM-<VENDOR>-<MODEL>).';
COMMENT ON COLUMN public.products.product_name IS 'Commercial hardware model name and configuration.';
COMMENT ON COLUMN public.products.vendor IS 'Original Equipment Manufacturer (OEM) brand name.';
COMMENT ON COLUMN public.products.category IS 'IT distribution product category (Laptops, Enterprise Servers, Networking, AI Accelerators, Storage, Peripherals).';
COMMENT ON COLUMN public.products.unit_cost_usd IS 'Distributor wholesale acquisition cost per unit in USD.';
COMMENT ON COLUMN public.products.unit_price_usd IS 'Standard B2B reseller catalog list price per unit in USD before partner tier discounts.';
COMMENT ON COLUMN public.products.active IS 'Whether the SKU is actively available for reseller ordering.';
COMMENT ON COLUMN public.products.updated_at IS 'Timestamp of last catalog price or status update.';

CREATE TABLE public.product_transactions (
    transaction_id VARCHAR(32) PRIMARY KEY,
    sku VARCHAR(32) NOT NULL REFERENCES public.products(sku),
    reseller_name VARCHAR(128) NOT NULL,
    sales_region VARCHAR(32) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    discount_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00 CHECK (discount_pct >= 0 AND discount_pct <= 100),
    transaction_ts TIMESTAMPTZ NOT NULL,
    order_status VARCHAR(24) NOT NULL CHECK (order_status IN ('COMPLETED', 'SHIPPED', 'RETURNED'))
);

COMMENT ON TABLE public.product_transactions IS 'Ingram Micro B2B reseller purchase order line transactions referencing catalog SKUs.';
COMMENT ON COLUMN public.product_transactions.transaction_id IS 'Unique B2B reseller order line transaction identifier.';
COMMENT ON COLUMN public.product_transactions.sku IS 'Catalog SKU ordered by the reseller (foreign key to public.products.sku).';
COMMENT ON COLUMN public.product_transactions.reseller_name IS 'Authorized channel partner or value-added reseller (VAR) name.';
COMMENT ON COLUMN public.product_transactions.sales_region IS 'Geographic distribution sales territory (AMER-West, AMER-East, EMEA, APAC).';
COMMENT ON COLUMN public.product_transactions.quantity IS 'Number of hardware units ordered on this transaction line.';
COMMENT ON COLUMN public.product_transactions.discount_pct IS 'Partner tier percentage discount off unit_price_usd (0 to 100).';
COMMENT ON COLUMN public.product_transactions.transaction_ts IS 'UTC timestamp when the reseller order transaction was booked.';
COMMENT ON COLUMN public.product_transactions.order_status IS 'Fulfillment lifecycle status: COMPLETED, SHIPPED, or RETURNED (RETURNED excluded from recognized revenue).';

INSERT INTO public.products (sku, product_name, vendor, category, unit_cost_usd, unit_price_usd, active) VALUES
('IM-LNV-T14G5',  'ThinkPad T14 Gen 5 Core Ultra 7 32GB/1TB',      'Lenovo',   'Laptops',            1120.00, 1399.00, TRUE),
('IM-HP-EB840',   'EliteBook 840 G11 14in Enterprise Notebook',    'HP',       'Laptops',            1080.00, 1349.00, TRUE),
('IM-APL-MBP16',  'MacBook Pro 16in Pro Chip 36GB/1TB',            'Apple',    'Laptops',            2190.00, 2599.00, TRUE),
('IM-DLL-R760',   'PowerEdge R760 2U Dual Xeon Rack Server',       'Dell',     'Enterprise Servers', 6850.00, 8499.00, TRUE),
('IM-HPE-DL380',  'ProLiant DL380 Gen11 2U Compute Server',        'HPE',      'Enterprise Servers', 6400.00, 7950.00, TRUE),
('IM-NVDA-L40S',  'L40S 48GB PCIe Data Center AI Accelerator',     'NVIDIA',   'AI Accelerators',    7900.00, 9650.00, TRUE),
('IM-CSC-C9300',  'Catalyst 9300 48-Port PoE+ Managed Switch',     'Cisco',    'Networking',         4350.00, 5490.00, TRUE),
('IM-ANET-7050X', '7050X4 400G Leaf Data Center Switch',           'Arista',   'Networking',         8200.00, 10200.00, TRUE),
('IM-SAM-990P4T', '990 PRO 4TB PCIe 4.0 NVMe Enterprise SSD',      'Samsung',  'Storage',             265.00,   349.00, TRUE),
('IM-LOG-MX3S',   'MX Master 3S for Business Wireless Mouse',      'Logitech', 'Peripherals',          72.00,    99.00, TRUE);

INSERT INTO public.product_transactions (transaction_id, sku, reseller_name, sales_region, quantity, discount_pct, transaction_ts, order_status) VALUES
('TXN-2026-1001', 'IM-LNV-T14G5',  'CDW Corporation',          'AMER-East', 45,  8.00, '2026-11-01 14:20:00+00', 'COMPLETED'),
('TXN-2026-1002', 'IM-DLL-R760',   'World Wide Technology',    'AMER-West', 12, 10.00, '2026-11-02 16:05:00+00', 'COMPLETED'),
('TXN-2026-1003', 'IM-NVDA-L40S',  'Presidio',                 'AMER-West', 16,  6.50, '2026-11-03 18:30:00+00', 'COMPLETED'),
('TXN-2026-1004', 'IM-CSC-C9300',  'Insight Enterprises',      'EMEA',      20,  9.00, '2026-11-04 10:15:00+00', 'COMPLETED'),
('TXN-2026-1005', 'IM-APL-MBP16',  'SHI International',        'AMER-East', 30,  5.00, '2026-11-05 15:40:00+00', 'COMPLETED'),
('TXN-2026-1006', 'IM-SAM-990P4T', 'Zones LLC',                'AMER-West', 120, 7.50, '2026-11-06 19:10:00+00', 'COMPLETED'),
('TXN-2026-1007', 'IM-HP-EB840',   'CDW Corporation',          'AMER-East', 60,  8.50, '2026-11-07 13:50:00+00', 'COMPLETED'),
('TXN-2026-1008', 'IM-HPE-DL380',  'Computacenter',            'EMEA',      10,  9.50, '2026-11-08 09:25:00+00', 'COMPLETED'),
('TXN-2026-1009', 'IM-ANET-7050X', 'World Wide Technology',    'AMER-West',  8,  7.00, '2026-11-09 17:00:00+00', 'COMPLETED'),
('TXN-2026-1010', 'IM-LOG-MX3S',   'Insight Enterprises',      'APAC',      200, 12.00, '2026-11-10 04:30:00+00', 'COMPLETED'),
('TXN-2026-1011', 'IM-NVDA-L40S',  'SHI International',        'AMER-East', 24,  7.50, '2026-11-11 16:45:00+00', 'COMPLETED'),
('TXN-2026-1012', 'IM-LNV-T14G5',  'Bechtle AG',               'EMEA',      50,  9.00, '2026-11-12 11:20:00+00', 'COMPLETED'),
('TXN-2026-1013', 'IM-DLL-R760',   'Presidio',                 'AMER-East',  8,  8.00, '2026-11-12 20:15:00+00', 'RETURNED'),
('TXN-2026-1014', 'IM-CSC-C9300',  'CDW Corporation',          'AMER-West', 25, 10.00, '2026-11-13 15:10:00+00', 'COMPLETED'),
('TXN-2026-1015', 'IM-APL-MBP16',  'Datacom Group',            'APAC',      22,  5.50, '2026-11-14 03:45:00+00', 'SHIPPED'),
('TXN-2026-1016', 'IM-HPE-DL380',  'Insight Enterprises',      'AMER-West', 14,  9.00, '2026-11-14 18:20:00+00', 'SHIPPED'),
('TXN-2026-1017', 'IM-SAM-990P4T', 'SHI International',        'AMER-East', 150, 8.00, '2026-11-15 14:00:00+00', 'SHIPPED'),
('TXN-2026-1018', 'IM-ANET-7050X', 'Presidio',                 'AMER-East',  6,  6.00, '2026-11-15 21:30:00+00', 'SHIPPED'),
('TXN-2026-1019', 'IM-HP-EB840',   'Zones LLC',                'AMER-West', 35,  7.00, '2026-11-16 16:10:00+00', 'SHIPPED'),
('TXN-2026-1020', 'IM-LOG-MX3S',   'CDW Corporation',          'AMER-East', 100, 10.00, '2026-11-16 19:45:00+00', 'RETURNED');
