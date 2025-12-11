-- UTF-8 인코딩 설정
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE DATABASE IF NOT EXISTS enterprise_hr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE enterprise_hr_db;

-- 1. 부서 정보
CREATE TABLE IF NOT EXISTS departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    location VARCHAR(50)
);

-- 2. 직원 정보 (핵심 마스터 데이터)
CREATE TABLE IF NOT EXISTS employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    dept_id INT,
    position VARCHAR(50), -- 사원, 대리, 과장, 팀장
    join_date DATE,
    status ENUM('ACTIVE', 'LEAVE', 'RESIGNED') DEFAULT 'ACTIVE',
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 3. 급여 정보 (숫자 분석용)
CREATE TABLE IF NOT EXISTS salaries (
    salary_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT,
    base_salary INT, -- 기본급
    bonus INT,       -- 보너스
    payment_date DATE,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 4. 성과 평가 (텍스트 + 숫자 - Multi Agent 타겟)
CREATE TABLE IF NOT EXISTS evaluations (
    eval_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT,
    year INT,
    quarter INT, -- 1~4분기
    score DECIMAL(3, 1), -- 5.0 만점
    feedback TEXT, -- "리더십이 뛰어나나 기술적 깊이 보완 필요" (RAG/검색용)
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 5. 근태 기록 (이상 감지용)
CREATE TABLE IF NOT EXISTS attendance (
    att_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT,
    date DATE,
    check_in TIME,
    check_out TIME,
    status ENUM('PRESENT', 'LATE', 'ABSENT', 'VACATION'),
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 더미 데이터 삽입
INSERT INTO departments (name, location) VALUES
('개발', '서울'), ('영업', '부산'), ('인사', '서울');

INSERT INTO employees (name, email, dept_id, position, join_date, status) VALUES
('김철수', 'cs.kim@techcorp.com', 1, 'Team Lead', '2020-01-10', 'ACTIVE'),
('이영희', 'yh.lee@techcorp.com', 1, 'Senior Engineer', '2021-03-15', 'ACTIVE'),
('박민수', 'ms.park@techcorp.com', 2, 'Sales Manager', '2019-11-01', 'ACTIVE'),
('최지우', 'jw.choi@techcorp.com', 3, 'HR Specialist', '2022-07-20', 'LEAVE');

INSERT INTO salaries (emp_id, base_salary, bonus, payment_date) VALUES
(1, 8000000, 2000000, '2023-12-25'),
(2, 6000000, 500000, '2023-12-25'),
(3, 7000000, 3000000, '2023-12-25'),
(4, 4500000, 0, '2023-12-25');

INSERT INTO evaluations (emp_id, year, quarter, score, feedback) VALUES
(1, 2023, 4, 4.8, '팀원들의 멘토링을 훌륭하게 수행함. 프로젝트 납기를 준수함.'),
(2, 2023, 4, 4.2, '기술적 역량은 뛰어나나 커뮤니케이션 스킬 향상이 필요함.'),
(3, 2023, 4, 4.9, '분기 매출 목표를 150% 달성함. 탁월한 영업 성과.'),
(4, 2023, 3, 3.5, '업무 습득 속도가 다소 느림. 적극적인 태도 필요.');

INSERT INTO attendance (emp_id, date, check_in, check_out, status) VALUES
-- 김철수 (4건)
(1, '2024-01-02', '08:55', '18:10', 'PRESENT'),
(1, '2024-01-03', '09:15', '18:30', 'LATE'),
(1, '2024-01-04', '08:50', '18:00', 'PRESENT'),
(1, '2024-01-05', NULL, NULL, 'VACATION'),
-- 이영희 (4건)
(2, '2024-01-02', '08:45', '18:05', 'PRESENT'),
(2, '2024-01-03', '08:50', '18:20', 'PRESENT'),
(2, '2024-01-04', '09:20', '18:15', 'LATE'),
(2, '2024-01-05', '08:55', '18:00', 'PRESENT'),
-- 박민수 (4건)
(3, '2024-01-02', '09:00', '19:00', 'PRESENT'),
(3, '2024-01-03', NULL, NULL, 'ABSENT'),
(3, '2024-01-04', '08:40', '18:30', 'PRESENT'),
(3, '2024-01-05', '08:55', '18:10', 'PRESENT'),
-- 최지우 (3건 - 휴직 중이라 적음)
(4, '2024-01-02', '09:00', '18:00', 'PRESENT'),
(4, '2024-01-03', '08:50', '18:05', 'PRESENT'),
(4, '2024-01-04', NULL, NULL, 'VACATION');


