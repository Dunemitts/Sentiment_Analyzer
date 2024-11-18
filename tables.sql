DROP TABLE hotels;
TRUNCATE TABLE hotels;
DROP TABLE ratings;
TRUNCATE TABLE ratings;
DROP DIRECTORY processed_data_dir;

CREATE OR REPLACE DIRECTORY processed_data_dir AS 'C:\Users\13178\Documents\GitHub\Sentiment_Analyzer';

SELECT directory_name, directory_path FROM ALL_DIRECTORIES WHERE directory_name like 'PROCESSED_DATA_DIR';
SELECT directory_path || '/' || 'Hotels.csv' FROM ALL_DIRECTORIES WHERE directory_name = 'PROCESSED_DATA_DIR';

-- Create the hotels table (representing a single hotel)
CREATE TABLE hotels (
    HOTELID NUMBER(38, 0) PRIMARY KEY,    
    NAME    VARCHAR2(100) NOT NULL,  
    CITY    VARCHAR2(100),
    COUNTRY VARCHAR2(100)
);

SELECT * FROM(SELECT * FROM  hotels ORDER BY DBMS_RANDOM.RANDOM) WHERE  rownum < 6;
SELECT COUNT(*) FROM hotels;
SELECT COUNT(*) FROM user_tables WHERE table_name = 'HOTELS';
SELECT HOTELID, NAME, CITY FROM hotels WHERE NAME = 'Unknown';

CREATE TABLE ratings (
    RATINGID INT PRIMARY KEY,
    HOTELID INT,
    BREAKFASTSCORE INT,
    CLEANSCORE INT,
    PRICESCORE INT,
    SERVICESCORE INT,
    LOCALSCORE INT,
    FOREIGN KEY (HOTELID) REFERENCES hotels(HOTELID)
);

SELECT * FROM(SELECT * FROM  ratings ORDER BY DBMS_RANDOM.RANDOM) WHERE  rownum < 6;
SELECT COUNT(*) FROM ratings;
SELECT COUNT(*) FROM user_tables WHERE table_name = 'RATINGS';


DECLARE
    fh_hotels    UTL_FILE.FILE_TYPE;
    v_line       VARCHAR2(4000);
    v_hotelid    NUMBER;
    v_name       VARCHAR2(100);
    v_city       VARCHAR2(100);
    v_country    VARCHAR2(100);
    v_hotel_count NUMBER := 0;

BEGIN

    DBMS_OUTPUT.PUT_LINE('Starting Hotels file processing...');
    DBMS_OUTPUT.PUT_LINE('Full path to Hotels.csv: ' || 'PROCESSED_DATA_DIR' || '/' || 'Hotels.csv');
    -- C:\Users\13178\Documents\GitHub\Sentiment_Analyzer\Hotels.csv
    -- C:\Users\13178\Documents\GitHub\Sentiment_Analyzer\tables.sql

    BEGIN
        fh_hotels := UTL_FILE.FOPEN('PROCESSED_DATA_DIR', 'Hotels.csv', 'r');
        DBMS_OUTPUT.PUT_LINE('Opened Hotels file.');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Exception: SQLCODE=' || SQLCODE || '  SQLERRM=' || SQLERRM);
            RAISE;
    END;

    LOOP
        BEGIN
            UTL_FILE.GET_LINE(fh_hotels, v_line);
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                EXIT;
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('Error reading Hotels file: ' || SQLERRM);
                EXIT;
        END;

        IF REGEXP_LIKE(v_line, '^\d+') THEN
            v_hotelid := TO_NUMBER(REGEXP_SUBSTR(v_line, '^[^,]+'));
        ELSE
            CONTINUE;
        END IF;
        v_name := REGEXP_SUBSTR(v_line, '[^,]+', 1, 2);  
        v_city := REGEXP_SUBSTR(v_line, '[^,]+', 1, 3); 
        v_country := REGEXP_SUBSTR(v_line, '[^,]+', 1, 4); 

        IF v_name IS NULL OR v_city IS NULL OR v_country IS NULL THEN
            CONTINUE;  
        END IF;

        BEGIN
            INSERT INTO hotels (HOTELID, NAME, CITY, COUNTRY)
            VALUES (v_hotelid, v_name, v_city, v_country);
            
            v_hotel_count := v_hotel_count + 1;
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('Error inserting hotel record: ' || SQLERRM || ' for line: ' || v_line);
        END;
    END LOOP;

    UTL_FILE.FCLOSE(fh_hotels);
    DBMS_OUTPUT.PUT_LINE('Closed Hotels file.');

    COMMIT;

    DBMS_OUTPUT.PUT_LINE('Hotels file processing completed. Total Hotels Inserted: ' || v_hotel_count);

EXCEPTION
    WHEN OTHERS THEN
        BEGIN
            UTL_FILE.FCLOSE(fh_hotels);
        EXCEPTION WHEN OTHERS THEN NULL; END;
        RAISE;
END;
/

CREATE SEQUENCE Ratings_SEQ
START WITH 1
INCREMENT BY 1
NOCACHE;

DECLARE
    fh_reviews   UTL_FILE.FILE_TYPE;     

    v_idreview   ratings.IDREVIEW%TYPE;  
    v_hotelid    ratings.HOTELID%TYPE;
    v_breakfast_score   ratings.BREAKFASTSCORE%TYPE;
    v_clean_score   ratings.CLEANSCORE%TYPE;
    v_price_score         ratings.PRICESCORE%TYPE;
    v_service_score       ratings.SERVICESCORE%TYPE;
    v_local_score      ratings.LOCALSCORE%TYPE;
    v_line       VARCHAR2(4000);         
    v_rating_count NUMBER := 0;  

BEGIN
    DBMS_OUTPUT.PUT_LINE('Starting Ratings file processing...');
    BEGIN
        fh_reviews := UTL_FILE.FOPEN('processed_data_dir', 'processed_reviews_output.csv', 'r');
        DBMS_OUTPUT.PUT_LINE('Opened Ratings file.');
    EXCEPTION
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Error opening Ratings file: ' || SQLERRM);
            RAISE;
    END;
    LOOP
        BEGIN
            UTL_FILE.GET_LINE(fh_reviews, v_line);
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                EXIT;  
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('Error reading Ratings file: ' || SQLERRM);
                EXIT;
        END;
        BEGIN
            v_idreview := TO_NUMBER(REGEXP_SUBSTR(v_line, '^[^,]+'));           
            v_hotelid := TO_NUMBER(REGEXP_SUBSTR(v_line, '[^,]+', 1, 2));       
            v_cleanliness_score := TO_NUMBER(REGEXP_SUBSTR(v_line, '[^,]+', 1, 3)); 
            v_price_score := TO_NUMBER(REGEXP_SUBSTR(v_line, '[^,]+', 1, 4));      
            v_service_score := TO_NUMBER(REGEXP_SUBSTR(v_line, '[^,]+', 1, 5));    
            v_location_score := TO_NUMBER(REGEXP_SUBSTR(v_line, '[^,]+', 1, 6));   
            IF v_idreview IS NULL OR v_hotelid IS NULL OR v_cleanliness_score IS NULL OR 
               v_price_score IS NULL OR v_service_score IS NULL OR v_location_score IS NULL THEN
                CONTINUE; 
            END IF;
            BEGIN
                INSERT INTO Ratings (RATINGID, IDREVIEW, HOTELID, CleanlinessScore, PriceScore, ServiceScore, LocationScore)
                VALUES (Ratings_SEQ.NEXTVAL, v_idreview, v_hotelid, v_cleanliness_score, v_price_score, v_service_score, v_location_score);
                v_rating_count := v_rating_count + 1;
            EXCEPTION
                WHEN OTHERS THEN
                    DBMS_OUTPUT.PUT_LINE('Error inserting rating record: ' || SQLERRM || ' for line: ' || v_line);
            END;
        END; 
    END LOOP;
    UTL_FILE.FCLOSE(fh_reviews);
    DBMS_OUTPUT.PUT_LINE('Closed Ratings file.');
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Ratings file processing completed. Total Ratings Inserted: ' || v_rating_count);
EXCEPTION
    WHEN OTHERS THEN
        BEGIN
            UTL_FILE.FCLOSE(fh_reviews);
        EXCEPTION WHEN OTHERS THEN NULL; END;
        RAISE;
END;
/

CREATE TABLE RATINGSAVERAGE (
    HOTELID NUMBER(38,0),
    AVERAGE_BREAKFASTSCORE NUMBER(38,0),
    AVERAGE_CLEANSCORE NUMBER(38,0),
    AVERAGE_PRICESCORE NUMBER(38,0),
    AVERAGE_SERVICESCORE NUMBER(38,0),
    AVERAGE_LOCALSCORE NUMBER(38,0)
);

INSERT INTO RATINGSAVERAGE (HOTELID, AVERAGE_BREAKFASTSCORE, AVERAGE_CLEANSCORE, AVERAGE_PRICESCORE, AVERAGE_SERVICESCORE, AVERAGE_LOCALSCORE)
SELECT 
    HOTELID,
    ROUND(AVG(BREAKFASTSCORE), 0) AS AVERAGE_BREAKFASTSCORE,
    ROUND(AVG(CLEANSCORE), 0) AS AVERAGE_CLEANSCORE,
    ROUND(AVG(PRICESCORE), 0) AS AVERAGE_PRICESCORE,
    ROUND(AVG(SERVICESCORE), 0) AS AVERAGE_SERVICESCORE,
    ROUND(AVG(LOCALSCORE), 0) AS AVERAGE_LOCALSCORE
FROM RATINGS
GROUP BY HOTELID
ORDER BY HOTELID;

select * from ratingsaverage;

SELECT HOTELID, AVERAGE_CLEANLINESSSCORE, AVERAGE_PRICESCORE,
       AVERAGE_SERVICESCORE, AVERAGE_LOCATIONSCORE FROM RATINGSAVERAGE
