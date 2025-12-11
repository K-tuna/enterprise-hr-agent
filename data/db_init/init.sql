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
-- 개발팀 (5명)
('김철수', 'cs.kim@techcorp.com', 1, '부장', '2015-03-10', 'ACTIVE'),
('이영희', 'yh.lee@techcorp.com', 1, '과장', '2018-06-15', 'ACTIVE'),
('정하늘', 'hn.jung@techcorp.com', 1, '대리', '2021-02-01', 'ACTIVE'),
('강민재', 'mj.kang@techcorp.com', 1, '사원', '2023-01-09', 'ACTIVE'),
('윤서연', 'sy.yoon@techcorp.com', 1, '사원', '2023-08-14', 'ACTIVE'),
-- 영업팀 (5명)
('박민수', 'ms.park@techcorp.com', 2, '부장', '2014-05-20', 'ACTIVE'),
('한지민', 'jm.han@techcorp.com', 2, '과장', '2017-09-01', 'ACTIVE'),
('오준혁', 'jh.oh@techcorp.com', 2, '대리', '2020-04-13', 'ACTIVE'),
('신유나', 'yn.shin@techcorp.com', 2, '사원', '2022-11-07', 'ACTIVE'),
('임도현', 'dh.lim@techcorp.com', 2, '사원', '2024-01-02', 'ACTIVE'),
-- 인사팀 (5명)
('최지우', 'jw.choi@techcorp.com', 3, '부장', '2013-08-15', 'ACTIVE'),
('조예린', 'yr.jo@techcorp.com', 3, '과장', '2016-12-01', 'LEAVE'),
('배성훈', 'sh.bae@techcorp.com', 3, '대리', '2019-07-22', 'ACTIVE'),
('문지영', 'jy.moon@techcorp.com', 3, '사원', '2022-03-14', 'ACTIVE'),
('류태민', 'tm.ryu@techcorp.com', 3, '사원', '2023-05-08', 'ACTIVE');

INSERT INTO salaries (emp_id, base_salary, bonus, payment_date) VALUES
-- 개발팀
(1, 9500000, 3000000, '2024-01-25'),
(2, 7000000, 1500000, '2024-01-25'),
(3, 5000000, 800000, '2024-01-25'),
(4, 3800000, 300000, '2024-01-25'),
(5, 3500000, 0, '2024-01-25'),
-- 영업팀
(6, 9000000, 5000000, '2024-01-25'),
(7, 6500000, 2000000, '2024-01-25'),
(8, 4800000, 1200000, '2024-01-25'),
(9, 3600000, 500000, '2024-01-25'),
(10, 3200000, 0, '2024-01-25'),
-- 인사팀
(11, 8500000, 2000000, '2024-01-25'),
(12, 6000000, 1000000, '2024-01-25'),
(13, 4500000, 600000, '2024-01-25'),
(14, 3400000, 200000, '2024-01-25'),
(15, 3300000, 0, '2024-01-25');

INSERT INTO evaluations (emp_id, year, quarter, score, feedback) VALUES
(1, 2023, 4, 4.8, '팀원들의 멘토링을 훌륭하게 수행함. 프로젝트 납기를 준수함.'),
(2, 2023, 4, 4.2, '기술적 역량은 뛰어나나 커뮤니케이션 스킬 향상이 필요함.'),
(3, 2023, 4, 4.5, '신규 프로젝트 리드로서 안정적인 성과를 보임.'),
(4, 2023, 4, 3.8, '성실한 태도로 업무에 임함. 기술 역량 향상 중.'),
(5, 2023, 4, 3.5, '신입으로서 적응 중. 학습 속도가 빠름.'),
(6, 2023, 4, 4.9, '분기 매출 목표를 150% 달성함. 탁월한 영업 성과.'),
(7, 2023, 4, 4.3, '주요 거래처 관리를 잘 수행함. 후배 육성에도 기여.'),
(8, 2023, 4, 4.0, '꾸준한 실적 유지. 신규 고객 발굴 노력 필요.'),
(9, 2023, 4, 3.7, '적극적인 영업 활동. 성과로 이어지는 중.'),
(10, 2023, 4, 3.2, '신입 교육 과정 중. 기본기 습득에 집중.'),
(11, 2023, 4, 4.6, '인사 제도 개선에 크게 기여함. 리더십 우수.'),
(12, 2023, 3, 3.5, '업무 습득 속도가 다소 느림. 적극적인 태도 필요.'),
(13, 2023, 4, 4.1, '채용 프로세스 효율화에 기여. 꼼꼼한 업무 처리.'),
(14, 2023, 4, 3.9, '교육 프로그램 운영을 잘 수행함.'),
(15, 2023, 4, 3.6, '성실하게 업무 수행 중. 전문성 향상 기대.');

INSERT INTO attendance (emp_id, date, check_in, check_out, status) VALUES
-- 김철수
(1, '2024-01-02', '08:55', '18:10', 'PRESENT'),
(1, '2024-01-03', '09:15', '18:30', 'LATE'),
(1, '2024-01-04', '08:50', '18:00', 'PRESENT'),
(1, '2024-01-05', NULL, NULL, 'VACATION'),
-- 이영희
(2, '2024-01-02', '08:45', '18:05', 'PRESENT'),
(2, '2024-01-03', '08:50', '18:20', 'PRESENT'),
(2, '2024-01-04', '09:20', '18:15', 'LATE'),
(2, '2024-01-05', '08:55', '18:00', 'PRESENT'),
-- 정하늘
(3, '2024-01-02', '08:50', '18:00', 'PRESENT'),
(3, '2024-01-03', '08:55', '18:10', 'PRESENT'),
(3, '2024-01-04', '08:45', '18:05', 'PRESENT'),
(3, '2024-01-05', '09:10', '18:20', 'LATE'),
-- 강민재
(4, '2024-01-02', '08:58', '18:00', 'PRESENT'),
(4, '2024-01-03', '08:55', '18:15', 'PRESENT'),
(4, '2024-01-04', NULL, NULL, 'VACATION'),
(4, '2024-01-05', '08:50', '18:00', 'PRESENT'),
-- 윤서연
(5, '2024-01-02', '09:05', '18:00', 'LATE'),
(5, '2024-01-03', '08:50', '18:10', 'PRESENT'),
(5, '2024-01-04', '08:55', '18:05', 'PRESENT'),
(5, '2024-01-05', '08:45', '18:00', 'PRESENT'),
-- 박민수
(6, '2024-01-02', '09:00', '19:00', 'PRESENT'),
(6, '2024-01-03', NULL, NULL, 'ABSENT'),
(6, '2024-01-04', '08:40', '18:30', 'PRESENT'),
(6, '2024-01-05', '08:55', '18:10', 'PRESENT'),
-- 한지민
(7, '2024-01-02', '08:50', '18:30', 'PRESENT'),
(7, '2024-01-03', '08:55', '19:00', 'PRESENT'),
(7, '2024-01-04', '09:05', '18:45', 'LATE'),
(7, '2024-01-05', '08:45', '18:20', 'PRESENT'),
-- 오준혁
(8, '2024-01-02', '08:55', '18:10', 'PRESENT'),
(8, '2024-01-03', '08:50', '18:00', 'PRESENT'),
(8, '2024-01-04', '08:58', '18:15', 'PRESENT'),
(8, '2024-01-05', NULL, NULL, 'VACATION'),
-- 신유나
(9, '2024-01-02', '08:45', '18:05', 'PRESENT'),
(9, '2024-01-03', '09:10', '18:20', 'LATE'),
(9, '2024-01-04', '08:50', '18:00', 'PRESENT'),
(9, '2024-01-05', '08:55', '18:10', 'PRESENT'),
-- 임도현
(10, '2024-01-02', '08:50', '18:00', 'PRESENT'),
(10, '2024-01-03', '08:55', '18:05', 'PRESENT'),
(10, '2024-01-04', '08:48', '18:00', 'PRESENT'),
(10, '2024-01-05', '08:52', '18:10', 'PRESENT'),
-- 최지우
(11, '2024-01-02', '09:00', '18:00', 'PRESENT'),
(11, '2024-01-03', '08:50', '18:05', 'PRESENT'),
(11, '2024-01-04', NULL, NULL, 'VACATION'),
(11, '2024-01-05', '08:55', '18:00', 'PRESENT'),
-- 조예린 (휴직 중이라 적음)
(12, '2024-01-02', '09:00', '18:00', 'PRESENT'),
(12, '2024-01-03', '08:55', '18:10', 'PRESENT'),
-- 배성훈
(13, '2024-01-02', '08:50', '18:05', 'PRESENT'),
(13, '2024-01-03', '08:45', '18:00', 'PRESENT'),
(13, '2024-01-04', '08:55', '18:10', 'PRESENT'),
(13, '2024-01-05', '09:15', '18:20', 'LATE'),
-- 문지영
(14, '2024-01-02', '08:55', '18:00', 'PRESENT'),
(14, '2024-01-03', '08:50', '18:05', 'PRESENT'),
(14, '2024-01-04', '08:58', '18:00', 'PRESENT'),
(14, '2024-01-05', NULL, NULL, 'VACATION'),
-- 류태민
(15, '2024-01-02', '08:48', '18:00', 'PRESENT'),
(15, '2024-01-03', '08:55', '18:10', 'PRESENT'),
(15, '2024-01-04', '08:50', '18:05', 'PRESENT'),
(15, '2024-01-05', '08:52', '18:00', 'PRESENT');


