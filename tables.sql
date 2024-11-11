-- Create the main table
DROP TABLE hotel_reviews;
TRUNCATE TABLE hotel_reviews;

CREATE TABLE hotel_reviews (
    id CHAR(3) PRIMARY KEY,
    idHotel CHAR(3),
    idReview CHAR(3),
    overall_sentiment CHAR(4),
    review VARCHAR2(4000)
);
SELECT * FROM hotel_reviews;
SELECT COUNT(*) FROM hotel_reviews;
SELECT COUNT(*) FROM user_tables WHERE table_name = 'HOTEL_REVIEWS';

