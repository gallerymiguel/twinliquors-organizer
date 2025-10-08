-- ================================
-- Twin Liquors Organizer Database
-- ================================

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item VARCHAR(255) NOT NULL,
  quantity INT NOT NULL DEFAULT 0,
  category VARCHAR(100),
  aisle VARCHAR(100),
  position VARCHAR(100),
  location_type VARCHAR(100),
  barcode VARCHAR(100),
  image_url VARCHAR(255),
  last_ordered DATE,
  active TINYINT(1) NOT NULL DEFAULT 1
);

-- Duties table
CREATE TABLE IF NOT EXISTS duties (
  id INT AUTO_INCREMENT PRIMARY KEY,
  task VARCHAR(255) NOT NULL,
  completed TINYINT(1) NOT NULL DEFAULT 0,
  date DATE NOT NULL
);

-- Name catalog table (for suggestions/autocomplete)
CREATE TABLE IF NOT EXISTS name_catalog (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE
);

-- ================================
-- Optional Seed Data (Development)
-- ================================

-- Inventory seeds
INSERT INTO inventory
(item, quantity, category, aisle, position, location_type, barcode, image_url, last_ordered, active)
VALUES
('Meiomi Pinot Noir', 5, 'Wine', NULL, NULL, 'shelf', NULL, NULL, '2025-08-01', 1),
('Casamigos Blanco', 2, 'Tequila', NULL, NULL, 'overstock', NULL, NULL, '2025-07-29', 1),
('Tito''s Vodka 750ml', 10, 'Vodka', 'A2', 'Top-Left', 'shelf', NULL, NULL, '2025-08-10', 1),
('Josh Cabernet', 1, 'Wine', NULL, NULL, 'overstock', NULL, NULL, '2025-08-08', 1);

-- Duties seeds
INSERT INTO duties (task, completed, date) VALUES
('Face whiskey aisle', 0, CURRENT_DATE()),
('Check chilled white restock', 0, CURRENT_DATE());
