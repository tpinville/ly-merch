-- Fashion Trends Database Schema

-- Verticals table (main categories like sneakers, sandals, etc.)
CREATE TABLE verticals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vertical_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    geo_zone VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_geo_zone (geo_zone),
    INDEX idx_vertical_id (vertical_id)
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

-- View to get all trends with their vertical information
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
    v.geo_zone
FROM trends t
JOIN verticals v ON t.vertical_id = v.id;

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
-- Get all sneaker trends for US market
SELECT * FROM trends_with_verticals
WHERE vertical_name LIKE '%sneakers%' AND geo_zone = 'us';

-- Find trends with most positive examples
SELECT trend_name, positive_image_count
FROM trend_image_stats
ORDER BY positive_image_count DESC;

-- Search trends by description
SELECT * FROM trends
WHERE MATCH(description) AGAINST('leather suede' IN BOOLEAN MODE);

-- Get all images for a specific trend
SELECT ti.image_type, ti.md5_hash, ti.description
FROM trend_images ti
JOIN trends t ON ti.trend_id = t.id
WHERE t.trend_id = 'b01441d690b4b5e4000f2fa90ba84268';
*/