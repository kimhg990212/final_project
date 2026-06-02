CREATE TABLE text_to_image_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    prompt TEXT NOT NULL,
    image_path VARCHAR(500) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);