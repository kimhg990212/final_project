CREATE TABLE IF NOT EXISTS  download_history (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  result_id BIGINT UNSIGNED NULL,
  prompt TEXT NOT NULL,
  image_path VARCHAR(500) NOT NULL,
  downloaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_download_history_user_id (user_id),
  KEY idx_download_history_result_id (result_id),
  KEY idx_download_history_downloaded_at (downloaded_at)
);

CREATE TABLE IF NOT EXISTS   detection_history (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  input_text TEXT NULL,
  uploaded_image_path VARCHAR(500) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_detection_history_user_id (user_id),
  KEY idx_detection_history_created_at (created_at),
  CONSTRAINT fk_detection_history_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS  detection_results (
  id INT NOT NULL AUTO_INCREMENT,
  history_id INT NOT NULL,
  trademark_id INT NOT NULL,
  similarity_score FLOAT NOT NULL,
  image_score FLOAT NULL,
  text_score FLOAT NULL,
  PRIMARY KEY (id),
  KEY idx_detection_results_history_id (history_id),
  KEY idx_detection_results_trademark_id (trademark_id),
  CONSTRAINT fk_detection_results_history
    FOREIGN KEY (history_id) REFERENCES detection_history(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_detection_results_trademark
    FOREIGN KEY (trademark_id) REFERENCES kipris_trademarks(id)
    ON DELETE CASCADE
);