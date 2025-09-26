-- Fashion Trends Database Schema

-- Categories table (main product categories extracted from vertical_id)
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);

-- Insert common categories based on vertical_id patterns
INSERT INTO categories (name, description) VALUES
('sneakers', 'Athletic and casual sneaker footwear'),
('sandals', 'Open-toed summer footwear and sandals'),
('dress_shoes', 'Formal dress shoes and professional footwear'),
('boots', 'Ankle boots, knee-high boots and winter footwear'),
('flats', 'Flat sole shoes including ballet flats and loafers'),
('heels', 'High-heeled footwear and pumps');

-- Verticals table (main categories like sneakers, sandals, etc.)
CREATE TABLE verticals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vertical_id VARCHAR(100) UNIQUE NOT NULL,
    category_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    geo_zone VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_geo_zone (geo_zone),
    INDEX idx_vertical_id (vertical_id),
    INDEX idx_category_id (category_id)
);

-- Trends table (specific trends within each vertical)
CREATE TABLE trends (
    id INT PRIMARY KEY AUTO_INCREMENT,
    trend_id VARCHAR(100) UNIQUE NOT NULL,
    vertical_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image_hash VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vertical_id) REFERENCES verticals(id) ON DELETE CASCADE,
    INDEX idx_trend_id (trend_id),
    INDEX idx_vertical_id (vertical_id),
    FULLTEXT idx_description (description),
    FULLTEXT idx_name (name)
);

-- Images table (stores both positive and negative example images)
CREATE TABLE trend_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    trend_id INT NOT NULL,
    image_type ENUM('positive', 'negative') NOT NULL,
    md5_hash VARCHAR(32) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (trend_id) REFERENCES trends(id) ON DELETE CASCADE,
    INDEX idx_trend_id (trend_id),
    INDEX idx_image_type (image_type),
    INDEX idx_md5_hash (md5_hash),
    UNIQUE KEY unique_trend_image (trend_id, md5_hash, image_type)
);

-- Create views for easier querying

-- View to get all trends with their vertical and category information
CREATE VIEW trends_with_verticals AS
SELECT
    t.id AS trend_id,
    t.trend_id AS trend_uuid,
    t.name AS trend_name,
    t.description AS trend_description,
    t.image_hash AS trend_image,
    v.id AS vertical_id,
    v.vertical_id AS vertical_uuid,
    v.name AS vertical_name,
    v.geo_zone,
    c.id AS category_id,
    c.name AS category_name,
    c.description AS category_description
FROM trends t
JOIN verticals v ON t.vertical_id = v.id
JOIN categories c ON v.category_id = c.id;

-- View to get image counts by trend
CREATE VIEW trend_image_stats AS
SELECT
    t.id AS trend_id,
    t.name AS trend_name,
    COUNT(CASE WHEN ti.image_type = 'positive' THEN 1 END) AS positive_image_count,
    COUNT(CASE WHEN ti.image_type = 'negative' THEN 1 END) AS negative_image_count,
    COUNT(*) AS total_images
FROM trends t
LEFT JOIN trend_images ti ON t.id = ti.trend_id
GROUP BY t.id, t.name;

-- Indexes for performance
CREATE INDEX idx_trends_name_fulltext ON trends(name);
CREATE INDEX idx_verticals_name ON verticals(name);
CREATE INDEX idx_trend_images_combined ON trend_images(trend_id, image_type);

-- Example queries for reference:

/*
-- Get all sneaker trends for US market using category
SELECT * FROM trends_with_verticals
WHERE category_name = 'sneakers' AND geo_zone = 'us';

-- Get all trends by category
SELECT category_name, COUNT(*) as trend_count
FROM trends_with_verticals
GROUP BY category_id, category_name
ORDER BY trend_count DESC;

-- Find trends with most positive examples
SELECT trend_name, positive_image_count, category_name
FROM trend_image_stats tis
JOIN trends_with_verticals twv ON tis.trend_id = twv.trend_id
ORDER BY positive_image_count DESC;

-- Search trends by description within a specific category
SELECT twv.*, t.description
FROM trends t
JOIN trends_with_verticals twv ON t.id = twv.trend_id
WHERE MATCH(t.description) AGAINST('leather suede' IN BOOLEAN MODE)
  AND twv.category_name = 'sneakers';

-- Get all images for a specific trend
SELECT ti.image_type, ti.md5_hash, ti.description
FROM trend_images ti
JOIN trends t ON ti.trend_id = t.id
WHERE t.trend_id = 'b01441d690b4b5e4000f2fa90ba84268';

-- Get all categories and their trend counts
SELECT
    c.name as category_name,
    c.description as category_description,
    COUNT(DISTINCT v.id) as vertical_count,
    COUNT(DISTINCT t.id) as trend_count
FROM categories c
LEFT JOIN verticals v ON c.id = v.category_id
LEFT JOIN trends t ON v.id = t.vertical_id
GROUP BY c.id, c.name, c.description
ORDER BY trend_count DESC;
*/