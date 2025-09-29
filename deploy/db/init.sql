create database if not exists personatalk;
use personatalk;

-- personatalk.history_session definition
drop table if exists `history_chat`;  -- 先删除子表
drop table if exists `history_session`;
CREATE TABLE `history_session` (
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `system_prompt` TEXT COLLATE utf8mb4_unicode_ci NOT NULL,  -- 改为 TEXT
  `voice_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_username` (`username`),  -- 添加索引
  INDEX `idx_is_deleted` (`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- personatalk.history_chat definition
CREATE TABLE `history_chat` (
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` TEXT COLLATE utf8mb4_unicode_ci NOT NULL,  -- 改为 TEXT
  PRIMARY KEY (`id`),
  INDEX `idx_session_id` (`session_id`),  -- 添加索引
  FOREIGN KEY (`session_id`) REFERENCES `history_session`(`id`) ON DELETE CASCADE  -- 添加外键
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;