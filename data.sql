
-- ===============================
-- 1️⃣ 插入 ProductAsset 数据 (4 条，已存在，可保留)
-- ===============================
INSERT INTO public.product_assets (id, type, type_id, texture_urls, created_at, updated_at) VALUES
(1, 'flat', 'SB-001', '{"SB-001": ["/api/media/textures/TX001.png"]}', NOW(), NOW()),
(2, 'camber', 'SB-002', '{"SB-002": ["/api/media/textures/TX002.png"]}', NOW(), NOW()),
(3, 'rocker', 'SB-003', '{"SB-003": ["/api/media/textures/TX003.png"]}', NOW(), NOW()),
(4, 'camber', 'SB-004', '{"SB-004": ["/api/media/textures/TX004.png"]}', NOW(), NOW());

-- ===============================
-- 2️⃣ 插入 Product 数据 (8 条)
-- ===============================

INSERT INTO public.products (id, name, type, status, price, p_desc, p_size, p_finish, p_flex, p_textures, is_double_sided, created_at, updated_at) VALUES
(1, 'Beginner Snowboard', 1, true, 199.90, '适合初学者的雪板', '150,155,160', 'matte,glossy', 'soft', '{"SB-001":["/api/media/textures/TX001.png"]}', true, NOW(), NOW()),
(2, 'Pro Snowboard', 1, true, 299.90, '专业级雪板，适合进阶滑手', '155,160,165', 'glossy', 'soft,regular', '{"SB-002":["/api/media/textures/TX002.png"]}', false, NOW(), NOW()),
(3, 'All-Mountain Snowboard', 1, true, 250.00, '适合多地形滑行的雪板', '148,153,158', 'matte', 'regular', '{"SB-003":["/api/media/textures/TX003.png"]}', false, NOW(), NOW()),
(4, 'Freestyle Snowboard', 1, true, 220.00, '适合自由式和公园滑行', '140,145,150', 'glossy', 'soft', '{"SB-004":["/api/media/textures/TX004.png"]}', false, NOW(), NOW()),
(5, 'Powder Snowboard', 1, true, 270.00, '专为深雪设计，浮力强', '155,160,165', 'matte,glossy', 'regular', '{"SB-001":["/api/media/textures/TX001.png"]}', false, NOW(), NOW()),
(6, 'Splitboard', 1, true, 320.00, '可拆分雪板，适合登山和下坡', '150,155,160', 'glossy', 'soft,regular', '{"SB-002":["/api/media/textures/TX002.png"]}', false, NOW(), NOW()),
(7, 'Carving Snowboard', 1, true, 280.00, '专为精准转弯设计，抓地力强', '148,153,158', 'matte', 'stiff', '{"SB-003":["/api/media/textures/TX003.png"]}', false, NOW(), NOW()),
(8, 'All-Rounder Snowboard', 1, true, 260.00, '适合全能滑手，多用途雪板', '150,155,160', 'glossy', 'soft,regular', '{"SB-004":["/api/media/textures/TX004.png"]}', false, NOW(), NOW());

-- ===============================
-- 3️⃣ 插入 ProductAssetLink 数据 (8 条，随机绑定资产)
-- ===============================
INSERT INTO public.product_asset_links (id, product_id, asset_id, quantity) VALUES
(1, 1, 1, 1),
(2, 2, 2, 1),
(3, 3, 3, 1),
(4, 4, 4, 1),
(5, 5, 1, 1),
(6, 6, 2, 1),
(7, 7, 3, 1),
(8, 8, 4, 1);
