-- Creates the database
create database herhealth;

-- Selects the database
use herhealth;

-- 
-- 1. TABLE DEFINITIONS
-- 

-- Stores user information
create table user (
    user_id int auto_increment primary key,
    f_name varchar(50),
    m_name varchar(50),
    l_name varchar(50) not null,
    email varchar(100) unique not null,
    phone varchar(15) not null,
    dob date,
    password varchar(100) not null,
    country varchar(50) default 'india',
    state varchar(50),
    city varchar(50),
    constraint chk_email check (email like '%@%')
);

-- Stores cycle tracking data
create table cycle (
    cycle_id int auto_increment primary key,
    user_id int,
    start_date date not null,
    end_date date,
    length int check (length > 0),
    mood_swings enum('none', 'mild', 'moderate', 'severe') default 'none',
    weight decimal(5,2) check (weight > 0),
    height decimal(5,2) check (height > 0),
    foreign key (user_id) references user(user_id) on delete cascade
);

-- Stores medication details
create table medicine (
    med_id int auto_increment primary key,
    cycle_id int,
    name_of_medicine varchar(100) not null,
    dosage varchar(50),
    doctor_consultation mediumblob,
    foreign key (cycle_id) references cycle(cycle_id) on delete cascade
);

-- Stores user notifications
create table notification (
    noti_id int auto_increment primary key,
    user_id int,
    start_date date,
    end_date date,
    medication_stock varchar(100),
    status enum('pending', 'sent', 'completed') default 'pending',
    foreign key (user_id) references user(user_id) on delete cascade
);

-- Stores cycle predictions
create table prediction (
    prediction_id int auto_increment primary key,
    cycle_id int,
    noti_id int,
    possible_start_start date,
    possible_start_end date,
    ovulation_date date,
    end date,
    length int check (length > 0),
    foreign key (cycle_id) references cycle(cycle_id) on delete cascade,
    foreign key (noti_id) references notification(noti_id) on delete cascade
);
  
-- Stores archived notifications
CREATE TABLE `notification_archive` (
  `noti_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `medication_stock` varchar(100) DEFAULT NULL,
  `status` varchar(10) DEFAULT 'archived',
  PRIMARY KEY (`noti_id`)
);

-- 
-- 2. TABLE MODIFICATIONS
-- 

-- Adds role to user
ALTER TABLE user ADD COLUMN role ENUM('user', 'admin') NOT NULL DEFAULT 'user';

-- Adds columns for file uploads
ALTER TABLE medicine
ADD COLUMN consultation_filename VARCHAR(255) NULL,
ADD COLUMN consultation_mimetype VARCHAR(100) NULL;


-- 
-- 3. DATA INSERTION
-- 

-- Inserts sample users
insert into user (f_name, m_name, l_name, email, phone, dob, password, country, state, city) values
('Geetha', 'Kumari', 'Sharma', 'geetha.sharma@email.com', '9876543210', '1995-03-15', 'hashed_password_1', 'India', 'Karnataka', 'Bangalore'),
('Mamata', 'Devi', 'Patel', 'mamata.patel@email.com', '9876543211', '1998-07-22', 'hashed_password_2', 'India', 'Gujarat', 'Ahmedabad'),
('Rephael', 'Mary', 'Johnson', 'rephael.j@email.com', '9876543212', '1993-11-08', 'hashed_password_3', 'India', 'Tamil Nadu', 'Chennai'),
('Janani', 'Lakshmi', 'Iyer', 'janani.iyer@email.com', '9876543213', '1997-05-30', 'hashed_password_4', 'India', 'Kerala', 'Kochi'),
('Bhavya', 'Sri', 'Reddy', 'bhavya.reddy@email.com', '9876543214', '2000-01-10', 'hashed_password_5', 'India', 'Telangana', 'Hyderabad');

-- Inserts admin users
insert into user (f_name,l_name, email, phone, dob, password, country, state, city,role) values
('Ankita', 'muni', 'ankitamuni2005@email.com', '8976543291', '2005-09-21', 'admin_password_1', 'India', 'Odisha', 'Bhubaneswar','admin'),
('Likitha', 'H', 'likithahlikithah@email.com', '9901476913', '2006-02-04', 'admin_password_2', 'India', 'Karnataka', 'Mandya','admin');

-- Inserts sample cycle data
insert into cycle (user_id, start_date, end_date, length, mood_swings, weight, height) values
(1, '2025-09-21', '2025-09-25', 5, 'mild', 55.50, 162.00),
(2, '2025-09-23', '2025-09-27', 5, 'moderate', 62.30, 158.50),
(3, '2025-09-25', '2025-09-30', 6, 'none', 58.70, 165.20),
(4, '2025-09-27', '2025-10-02', 6, 'severe', 61.00, 160.80),
(5, '2025-09-30', '2025-10-04', 5, 'mild', 59.20, 163.50);

-- Inserts sample medication data
insert into medicine (cycle_id, name_of_medicine, dosage, doctor_consultation) values
(1, 'Ibuprofen', '200mg twice daily', NULL),
(2, 'Mefenamic Acid', '500mg thrice daily', NULL),
(3, 'Dicyclomine', '10mg as needed', NULL),
(4, 'Combiflam', '1 tablet when pain occurs', NULL),
(5, 'Paracetamol', '650mg every 6 hours', NULL);

-- Inserts sample notification data
insert into notification (user_id, start_date, end_date, medication_stock, status) values
(1, '2025-10-22', '2025-10-26', 'Ibuprofen - 10 tablets left', 'pending'),
(2, '2025-10-24', '2025-10-28', 'Mefenamic Acid - 5 tablets left', 'sent'),
(3, '2025-10-26', '2025-10-31', 'Dicyclomine - 15 tablets left', 'completed'),
(4, '2025-10-28', '2025-11-02', 'Combiflam - 8 tablets left', 'pending'),
(5, '2025-10-31', '2025-11-04', 'Paracetamol - 12 tablets left', 'sent');

-- Inserts sample prediction data
insert into prediction (cycle_id, noti_id, possible_start_start, possible_start_end, ovulation_date, end, length) values
(1, 1, '2025-10-22', '2025-10-24', '2025-11-05', '2025-10-26', 5),
(2, 2, '2025-10-24', '2025-10-26', '2025-11-07', '2025-10-28', 5),
(3, 3, '2025-10-26', '2025-10-28', '2025-11-09', '2025-10-31', 6),
(4, 4, '2025-10-28', '2025-10-30', '2025-11-11', '2025-11-02', 6),
(5, 5, '2025-10-31', '2025-11-02', '2025-11-14', '2025-11-04', 5);


-- 
-- 4. DATA MODIFICATION (EXAMPLES)
-- 

-- Updates a cycle record
update cycle
set
    start_date = '2025-08-10',
    end_date = '2025-08-12',   
    length = 3                 
where
    user_id = 1 AND cycle_id = 1; 

-- Deletes a notification record
delete from notification
where noti_id = 3 and user_id = 3;


-- 
-- 5. FUNCTION DEFINITIONS
-- 

delimiter $$

-- Gets latest medication dosage
create function get_latest_medication_dosage (
    p_user_id int,
    p_med_name varchar(100)
)
returns varchar(50)
reads sql data
begin
    declare latest_dosage varchar(50);

    select m.dosage into latest_dosage
    from medicine m
    join cycle c on m.cycle_id = c.cycle_id
    where c.user_id = p_user_id
      and m.name_of_medicine = p_med_name
    order by c.start_date desc
    limit 1;

    return latest_dosage;
end$$

delimiter ;


-- 
-- 6. PROCEDURE DEFINITIONS
-- 

DELIMITER $$

-- Drops procedure if exists
DROP PROCEDURE IF EXISTS `archive_completed_notifications`;

-- Archives old notifications
CREATE PROCEDURE `archive_completed_notifications` (
    IN p_days_old INT
)
BEGIN
    DECLARE v_cutoff_date DATE;
    SET v_cutoff_date = DATE_SUB(CURDATE(), INTERVAL p_days_old DAY);

    -- Start transaction
    START TRANSACTION;

    -- Copy to archive
    INSERT INTO notification_archive (
        noti_id, 
        user_id, 
        start_date, 
        end_date, 
        medication_stock, 
        status
    )
    SELECT 
        noti_id, 
        user_id, 
        start_date, 
        end_date, 
        medication_stock, 
        'archived'
    FROM notification
    WHERE `status` = 'completed'
      AND `start_date` < v_cutoff_date;

    -- Delete from original
    DELETE FROM notification
    WHERE `status` = 'completed'
      AND `start_date` < v_cutoff_date;

    -- Commit changes
    COMMIT;
    
    -- Show rows affected
    SELECT ROW_COUNT() AS 'archived_count';

END$$

DELIMITER ;


-- 
-- 7. TRIGGER DEFINITIONS
-- 

delimiter $$

-- Sets prediction dates
create trigger before_insert_prediction_dates
before insert on prediction
for each row
begin
    declare notification_start_date date;
    declare notification_end_date date;

    select start_date, end_date
    into notification_start_date, notification_end_date
    from notification
    where noti_id = new.noti_id;

    if new.possible_start_start is null then
        set new.possible_start_start = notification_start_date;
    end if;

    if new.end is null then
        set new.end = notification_end_date;
    end if;

    if notification_start_date is not null and notification_end_date is not null then
        set new.length = datediff(notification_end_date, notification_start_date) + 1;
    end if;
end$$

delimiter ;


-- 
-- 8. EXAMPLE QUERIES (SELECTS)
-- 

-- Finds users over 35
select u.user_id, u.f_name, u.l_name, 
       datediff(curdate(), max(c.end_date)) as days_since_last_cycle
from user u
join cycle c on u.user_id = c.user_id
group by u.user_id
having days_since_last_cycle > 35;

-- Finds longest cycle
with cycle_rank as (
    select user_id, cycle_id, length,
           rank() over (partition by user_id order by length desc) as rnk
    from cycle
)
select u.f_name, u.l_name, c.length
from user u
join cycle_rank c on u.user_id = c.user_id
where c.rnk = 1;


-- Finds users missing data
select u.user_id, u.f_name, 'no notifications' as issue
from user u
left join notification n on u.user_id = n.user_id
where n.noti_id is null

union

select u.user_id, u.f_name, 'no medicines' as issue
from user u
left join cycle c on u.user_id = c.user_id
left join medicine m on c.cycle_id = m.cycle_id
where m.med_id is null;

-- Finds user with highest BMI
select
    u.user_id,
    concat(u.f_name, ' ', u.l_name) as full_name,
    u.city,
    round(avg(c.weight / (c.height / 100.0 * c.height / 100.0)), 2) as average_bmi
from
    user u
join
    cycle c on u.user_id = c.user_id
group by
    u.user_id, u.f_name, u.l_name, u.city 
order by
    average_bmi DESC
limit 1;

-- Finds meds for severe mood_swings
select
    c.cycle_id,
    c.start_date,
    c.mood_swings,
    m.name_of_medicine,
    m.dosage
from
    cycle c
join
    medicine m on c.cycle_id = m.cycle_id
where
    c.mood_swings = 'severe'
order by
    c.start_date desc;


-- Calculates user ages
select f_name, l_name, timestampdiff(year, dob, curdate()) as age from user;

-- Checks medication file uploads
SELECT 
    med_id, cycle_id, 
    name_of_medicine, 
    consultation_filename, 
    OCTET_LENGTH(doctor_consultation) AS file_size_in_bytes
FROM 
    medicine;


-- 
-- 9. PROCEDURE EXECUTION
-- 

-- Runs the archive procedure
CALL archive_completed_notifications(30);