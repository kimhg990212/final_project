
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `nickname` varchar(100) DEFAULT NULL,
  `role` varchar(20) DEFAULT 'USER',
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `google_sub` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `uk_users_google_sub` (`google_sub`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users`
(`id`, `email`, `password`, `nickname`, `role`, `is_deleted`, `created_at`)
VALUES
(1, 'test@test.com', '$2b$12$IzYI1m9JWLHVQK/eA2g3PO4X2S9W6uWY.e81RZPZGoc/1jxQoTpr.', 'kim', 'USER', 0, '2026-05-27 13:47:50');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
