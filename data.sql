
-- ===============================
-- 1️⃣ 插入 auth_user 数据 (1 条) admin
-- ===============================
INSERT INTO auth_user (id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (1, 'pbkdf2_sha256$390000$r13pZgwir1KqdAr0HZwTZs$cGqasRW44ADasr7tDk1l0YYF6TgvhPmUU0XyDoFHXLQ=', TRUE, 'admin', '', '', 'antareshx.whx@gmail.com', TRUE, TRUE, '2026-03-02 17:05:54.413432+00');


-- ===============================
-- 1️⃣ 插入 ProductAsset 数据 (4 条，已存在，可保留)
-- ===============================
INSERT INTO public.m_product_assets (id, type, asset_code, texture_urls, created_at, updated_at) VALUES
(1, 'flat', 'SB-001', '{"SB-001": ["/api/media/textures/TX001.png"]}', NOW(), NOW()),
(2, 'camber', 'SB-002', '{"SB-002": ["/api/media/textures/TX002.png"]}', NOW(), NOW()),
(3, 'rocker', 'SB-003', '{"SB-003": ["/api/media/textures/TX003.png"]}', NOW(), NOW()),
(4, 'camber', 'SB-004', '{"SB-004": ["/api/media/textures/TX004.png"]}', NOW(), NOW());

-- ===============================
-- 2️⃣ 插入 Product 数据 (8 条)
-- ===============================

INSERT INTO public.m_products (id, name, type, status, price, p_desc, p_size, p_finish, p_flex, p_textures, is_double_sided, created_at, updated_at) VALUES
(1, 'Beginner Snowboard', 1, true, 199.90, 'Ideal for beginners', '150,155,160', 'matte,glossy', 'soft', '{"SB-001":["/api/media/textures/TX001.png"]}', true, NOW(), NOW()),
(2, 'Pro Snowboard', 1, true, 299.90, 'Professional level snowboard for advanced riders', '155,160,165', 'glossy', 'soft,regular', '{"SB-002":["/api/media/textures/TX002.png"]}', false, NOW(), NOW()),
(3, 'All-Mountain Snowboard', 1, true, 250.00, 'Suitable for all-mountain riding', '148,153,158', 'matte', 'regular', '{"SB-003":["/api/media/textures/TX003.png"]}', false, NOW(), NOW()),
(4, 'Freestyle Snowboard', 1, true, 220.00, 'Perfect for freestyle and park riding', '140,145,150', 'glossy', 'soft', '{"SB-004":["/api/media/textures/TX004.png"]}', false, NOW(), NOW()),
(5, 'Powder Snowboard', 1, true, 270.00, 'Designed for deep powder snow', '155,160,165', 'matte,glossy', 'regular', '{"SB-001":["/api/media/textures/TX005.png"]}', false, NOW(), NOW()),
(6, 'Splitboard', 1, true, 320.00, 'Split snowboard for hiking and downhill', '150,155,160', 'glossy', 'soft,regular', '{"SB-002":["/api/media/textures/TX006.png"]}', false, NOW(), NOW()),
(7, 'Carving Snowboard', 1, true, 280.00, 'Designed for precise carving and grip', '148,153,158', 'matte', 'stiff', '{"SB-003":["/api/media/textures/TX007.png"]}', false, NOW(), NOW()),
(8, 'All-Rounder Snowboard', 1, true, 260.00, 'Versatile snowboard for all types of riders', '150,155,160', 'glossy', 'soft,regular', '{"SB-004":["/api/media/textures/TX001.png"]}', false, NOW(), NOW()),
(9, 'Backcountry Snowboard', 1, true, 310.00, 'Stable snowboard for backcountry riding', '155,160,165', 'matte', 'stiff', '{"SB-003":["/api/media/textures/TX002.png"]}', false, NOW(), NOW()),
(10, 'Junior Snowboard', 1, true, 180.00, 'Lightweight snowboard for kids and youth', '130,135,140', 'glossy', 'soft', '{"SB-004":["/api/media/textures/TX003.png"]}', true, NOW(), NOW());
-- ===============================
-- 3️⃣ 插入 ProductAssetLink 数据 (8 条，随机绑定资产)
-- ===============================
INSERT INTO public.m_product_asset_links (id, product_id, asset_id, quantity) VALUES
(1, 1, 1, 1),
(2, 2, 2, 1),
(3, 3, 3, 1),
(4, 4, 4, 1),
(5, 5, 1, 1),
(6, 6, 2, 1),
(7, 7, 3, 1),
(8, 8, 4, 1),
(9, 9, 3, 1),
(10, 10, 4, 1);


INSERT INTO m_user_profiles (id, clerk_id, email, name, address, created_at, updated_at)
VALUES
(100, 'clerk_100', 'alice@example.com', 'Alice Brown', 'London, UK', NOW(), NOW()),
(101, 'clerk_101', 'bob@example.com', 'Bob Smith', 'Manchester, UK', NOW(), NOW()),
(102, 'clerk_102', 'charlie@example.com', 'Charlie Green', 'Birmingham, UK', NOW(), NOW()),
(103, 'clerk_103', 'daisy@example.com', 'Daisy White', 'Glasgow, UK', NOW(), NOW()),
(104, 'clerk_104', 'ethan@example.com', 'Ethan Black', 'Liverpool, UK', NOW(), NOW());

INSERT INTO m_reviews (user_id, product_id, rating, comment, created_at)
VALUES
(100, 1, 5, 'Absolutely love this product! The quality is amazing.', NOW()),
(101, 1, 4, 'Very good overall, delivery was fast.', NOW()),
(102, 1, 5, 'Exceeded my expectations. Highly recommend!', NOW()),

(103, 2, 3, 'It is okay, but packaging could be better.', NOW()),
(104, 2, 4, 'Nice design and comfortable to use.', NOW()),
(100, 2, 5, 'Perfect gift idea. My friend loved it.', NOW()),

(101, 3, 2, 'Not exactly what I expected.', NOW()),
(102, 3, 4, 'Good value for money.', NOW()),
(103, 3, 5, 'Amazing craftsmanship!', NOW()),

(104, 1, 5, 'Will definitely buy again!', NOW()),
(100, 3, 4, 'Solid quality and fast shipping.', NOW()),
(101, 2, 5, 'Five stars. Everything was perfect.', NOW()),

(102, 2, 3, 'Average experience but decent support.', NOW()),
(103, 1, 4, 'Looks exactly like the pictures.', NOW()),
(104, 3, 5, 'Super satisfied with this purchase.', NOW());