
CREATE TABLE IF NOT EXISTS inventory (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item VARCHAR(255) NOT NULL,
  quantity INT NOT NULL DEFAULT 0,
  category VARCHAR(100),
  last_ordered DATE
);
CREATE TABLE IF NOT EXISTS duties (
  id INT AUTO_INCREMENT PRIMARY KEY,
  task VARCHAR(255) NOT NULL,
  completed TINYINT(1) NOT NULL DEFAULT 0,
  date DATE NOT NULL
);
INSERT INTO inventory (item, quantity, category, last_ordered) VALUES
('Meiomi Pinot Noir', 5, 'Wine', '2025-08-01'),
('Casamigos Blanco', 2, 'Tequila', '2025-07-29'),
('Tito''s Vodka 750ml', 10, 'Vodka', '2025-08-10'),
('Josh Cabernet', 1, 'Wine', '2025-08-08');
INSERT INTO duties (task, completed, date) VALUES
('Face whiskey aisle', 0, CURRENT_DATE()),
('Check chilled white restock', 0, CURRENT_DATE());
