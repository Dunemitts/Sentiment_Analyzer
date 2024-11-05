-- Create the main table
DROP TABLE hotel_reviews;
CREATE TABLE IF NOT EXISTS hotel_reviews (
    "id" CHAR(3) PRIMARY KEY,
    "idHotel" CHAR(3),
    "idReview" CHAR(3),
    "overall_sentiment" CHAR(3),
    "review" VARCHAR2(4000)
);
SELECT * FROM hotel_reviews;

-- Procedure to execute SQL statement
DROP PROCEDURE execute_sql;
CREATE OR REPLACE PROCEDURE execute_sql(p_sql_stmt IN CLOB) IS
BEGIN
    EXECUTE IMMEDIATE p_sql_stmt;
END;

-- Main script
DECLARE
  v_file_path VARCHAR2(4000) := 'processed_data/beijing/china_beijing_aloft_beijing_haidian_processed.csv';
  v_sql_stmt CLOB;
  v_count NUMBER := 0;
  v_total_rows NUMBER := 0;
  v_current_row NUMBER := 0;
  v_max_rows NUMBER := 10000; -- Adjust this value as needed
  
BEGIN
  -- Create table if it doesn't exist
  execute_sql('CREATE TABLE IF NOT EXISTS hotel_reviews (
                "id" CHAR(3) PRIMARY KEY,
                "idHotel" CHAR(3),
                "idReview" CHAR(3),
                "overall_sentiment" CHAR(3),
                "review" VARCHAR2(4000)
              )');

  -- Insert data from CSV file
  v_sql_stmt := 'INSERT INTO hotel_reviews ("id", "idHotel", "idReview", "overall_sentiment", "review")
                  SELECT 
                      LPAD(' || v_current_row || ', 3, ''0'') AS "id",
                      LPAD(1, 3, ''0'') AS "idHotel",
                      LPAD(' || v_current_row || ', 3, ''0'') AS "idReview",
                      LPAD(' || v_current_row || ', 3, ''0'') AS "overall_sentiment",
                      TRIM(REPLACE(SUBSTR(line, INSTR(line, '''', 1) + 1, INSTR(line, '''', -1) - INSTR(line, '''', 1) - 1)) || '''') AS "review"
                  FROM (
                      SELECT line, rownum rnum
                      FROM dba_source
                      WHERE owner = upper(''YOUR_SCHEMA_NAME'')
                        AND object_name = upper(''' || SUBSTR(v_file_path, INSTR(v_file_path, '/', 1) + 1, INSTR(v_file_path, '\', -1) - INSTR(v_file_path, '/', 1) - 1) || ''')
                  ) subquery';

  execute_sql(v_sql_stmt);

  -- Display progress
  DBMS_OUTPUT.PUT_LINE('Total rows processed: ' || TO_CHAR(v_count));

EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error occurred: ' || SQLERRM);
END;
/

-- Execute the procedure
BEGIN
  execute_sql('ALTER SESSION SET NLS_NUMERIC_CHARACTERS=''.,''');
  execute_sql('ALTER SESSION SET CURRENT_SCHEMA=' || UPPER(SYSDA.USER));
END;
/
