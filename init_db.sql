-- =====================================================
--  GIHUT TRAVEL DATABASE (LEVEL 3 PRO VERSION)
-- =====================================================

DROP DATABASE IF EXISTS travelsite;
CREATE DATABASE travelsite 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE travelsite;

-- ========== USERS ==========
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ========== CITIES ==========
CREATE TABLE cities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ========== ATTRACTIONS ==========
CREATE TABLE attractions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attraction_city FOREIGN KEY (city_id)
      REFERENCES cities(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
CREATE INDEX idx_attraction_city ON attractions(city_id);

-- ========== HOTELS ==========
CREATE TABLE hotels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    address TEXT,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hotel_city FOREIGN KEY (city_id)
      REFERENCES cities(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
CREATE INDEX idx_hotel_city ON hotels(city_id);

-- ========== BUSES ==========
CREATE TABLE buses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city_from INT NOT NULL,
    city_to INT NOT NULL,
    bus_name VARCHAR(100) NOT NULL,
    depart_time TIME NOT NULL,
    arrive_time TIME NOT NULL,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bus_from FOREIGN KEY (city_from) REFERENCES cities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_bus_to   FOREIGN KEY (city_to) REFERENCES cities(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
CREATE INDEX idx_bus_from ON buses(city_from);
CREATE INDEX idx_bus_to ON buses(city_to);

-- ========== BOOKINGS ==========
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    hotel_id INT NULL,
    bus_id INT NULL,
    checkin DATE,
    checkout DATE,
    seat_no VARCHAR(20),
    status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_booking_hotel FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_booking_bus FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;
CREATE INDEX idx_booking_user  ON bookings(user_id);
CREATE INDEX idx_booking_hotel ON bookings(hotel_id);
CREATE INDEX idx_booking_bus   ON bookings(bus_id);

-- ========== SAMPLE DATA ==========
INSERT INTO users (username,email,password,role)
VALUES ('admin','admin@gmail.com','$pbkdf2-sha256$260000$YOURLONGSALT..............','admin'); -- hashed, replace with own hash for production

INSERT INTO cities (name,description) VALUES
('Yangon','The largest city of Myanmar with colonial architecture'),
('Mandalay','Cultural capital of Myanmar');

INSERT INTO hotels (city_id,name,address,price) VALUES
(1,'Pan Pacific Yangon','Downtown Yangon',150000),
(2,'Mandalay Hill Resort','Near Mandalay Hill',120000);

INSERT INTO buses (city_from,city_to,bus_name,depart_time,arrive_time,price) VALUES
(1,2,'Elite Express','08:00:00','14:00:00',25000);

INSERT INTO attractions (city_id,name,description,image) VALUES
(1,'Shwedagon Pagoda','World famous pagoda located in Yangon.','shwedagon.jpg'),
(1,'Yangon Circular Train','Fun local train tour in Yangon.','circular_train.jpg'),
(2,'Mandalay Palace','Historic Mandalay Royal Palace.','mandalay_palace.jpg'),
(2,'Mandalay Hill','Well-known hilly attraction in Mandalay.','mandalay_hill.jpg');