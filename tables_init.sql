CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(512) DEFAULT NULL,
  `email` varchar(512) DEFAULT NULL,
  `password` varchar(512) DEFAULT NULL,
  `first_name` varchar(512) DEFAULT NULL,
  `last_name` varchar(512) DEFAULT NULL,
  `sso_id` varchar(512) DEFAULT NULL,
  `action_token` varchar(512) DEFAULT NULL,
  `last_password_change` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  `past_passwords_hash` text DEFAULT NULL,
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `auth_user_tag_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(512) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `record_id_fk` (`record_id`),
  CONSTRAINT `record_id_fk` FOREIGN KEY (`record_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `py4web_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rkey` varchar(512) DEFAULT NULL,
  `rvalue` text,
  `expiration` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `expires_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rkey__idx` (`rkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` text DEFAULT NULL,
  `name` text DEFAULT NULL,
  `permission` text DEFAULT NULL,
  `true_permission` text DEFAULT NULL,
  `view_all` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `planners` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `status` text DEFAULT NULL,
  `class_num` text DEFAULT NULL,
  `instruct_num` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `classes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `class_name` text DEFAULT NULL,
  `class_type` text DEFAULT NULL,
  `class_num` text DEFAULT NULL,
  `quarter_1` text DEFAULT NULL,
  `quarter_1_TA` text DEFAULT NULL,
  `quarter_1_size` text DEFAULT NULL,
  `quarter_2` text DEFAULT NULL,
  `quarter_2_TA` text DEFAULT NULL,
  `quarter_2_size` text DEFAULT NULL,
  `quarter_3` text DEFAULT NULL,
  `quarter_3_TA` text DEFAULT NULL,
  `quarter_3_size` text DEFAULT NULL,
  `summer_1` text DEFAULT NULL,
  `summer_1_TA` text DEFAULT NULL,
  `summer_1_size` text DEFAULT NULL,
  `summer_2` text DEFAULT NULL,
  `summer_2_TA` text DEFAULT NULL,
  `summer_2_size` text DEFAULT NULL,
  `course_time_sections` text DEFAULT NULL,

  `actual_times` text DEFAULT NULL,
  `planner_id` text DEFAULT NULL,

  `default_inst` text DEFAULT NULL,
  `default_quarters` text DEFAULT NULL,
  `class_sub` text DEFAULT NULL,
  `href` text DEFAULT NULL,
  `class_desc` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `instructors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` text DEFAULT NULL,
  `name` text DEFAULT NULL,
  `quarter_1` text DEFAULT NULL,
  `quarter_2` text DEFAULT NULL,
  `quarter_3` text DEFAULT NULL,
  `summer_1` text DEFAULT NULL,
  `summer_2` text DEFAULT NULL,
  `department` text DEFAULT NULL,
  `label` text DEFAULT NULL,
  `access` text DEFAULT NULL,
  `planner_id` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;