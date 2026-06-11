-- 1. RANKING
-- Ranking de clientes por saldo dentro de cada país
SELECT
    customer_id,
    surname,
    geography AS pais,
    balance AS saldo,
    RANK() OVER (PARTITION BY geography ORDER BY balance DESC) AS ranking_saldo_pais
FROM customers
ORDER BY geography, ranking_saldo_pais;

-- Ranking de clientes por credit score dentro de cada faixa etária
SELECT
    customer_id,
    surname,
    age,
    CASE
        WHEN age BETWEEN 18 AND 30 THEN '18-30'
        WHEN age BETWEEN 31 AND 45 THEN '31-45'
        WHEN age BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END AS faixa_etaria,
    credit_score,
    RANK() OVER (
        PARTITION BY
            CASE
                WHEN age BETWEEN 18 AND 30 THEN '18-30'
                WHEN age BETWEEN 31 AND 45 THEN '31-45'
                WHEN age BETWEEN 46 AND 60 THEN '46-60'
                ELSE '60+'
            END
        ORDER BY credit_score DESC
    ) AS ranking_score_faixa
FROM customers
ORDER BY faixa_etaria, ranking_score_faixa;

-- 2. COMPARAÇÃO COM MÉDIA
-- Saldo de cada cliente comparado com a média do seu país
SELECT
    customer_id,
    surname,
    geography AS pais,
    balance AS saldo,
    ROUND(AVG(balance) OVER (PARTITION BY geography)::numeric, 2) AS media_saldo_pais,
    ROUND((balance - AVG(balance) OVER (PARTITION BY geography))::numeric, 2) AS diferenca_da_media
FROM customers
ORDER BY geography, diferenca_da_media DESC;

-- Salário de cada cliente comparado com a média do seu gênero
SELECT
    customer_id,
    surname,
    gender AS genero,
    estimated_salary AS salario,
    ROUND(AVG(estimated_salary) OVER (PARTITION BY gender)::numeric, 2) AS media_salario_genero,
    ROUND((estimated_salary - AVG(estimated_salary) OVER (PARTITION BY gender))::numeric, 2) AS diferenca_da_media
FROM customers
ORDER BY gender, diferenca_da_media DESC;

-- 3. PERCENTIL
-- Percentil de saldo de cada cliente
SELECT
    customer_id,
    surname,
    credit_score,
    NTILE(4) OVER (ORDER BY credit_score) AS quartil_score,
    CASE NTILE(4) OVER (ORDER BY credit_score)
        WHEN 1 THEN 'Baixo'
        WHEN 2 THEN 'Médio-Baixo'
        WHEN 3 THEN 'Médio-Alto'
        WHEN 4 THEN 'Alto'
    END AS faixa_score,
    ROUND(PERCENT_RANK() OVER (ORDER BY credit_score)::numeric * 100, 2) AS percentil
FROM customers
ORDER BY credit_score DESC;

-- Percentil de credit score de cada cliente
SELECT
    customer_id,
    surname,
    credit_score,
    NTILE(4) OVER (ORDER BY credit_score) AS quartil_score,
    CASE NTILE(4) OVER (ORDER BY credit_score)
        WHEN 1 THEN 'Baixo'
        WHEN 2 THEN 'Médio-Baixo'
        WHEN 3 THEN 'Médio-Alto'
        WHEN 4 THEN 'Alto'
    END AS faixa_score,
    ROUND(PERCENT_RANK() OVER (ORDER BY credit_score) * 100, 2) AS percentil
FROM customers
ORDER BY credit_score DESC;

-- 4. ACUMULADO
-- Total acumulado de clientes por tenure
SELECT
    tenure AS anos_relacionamento,
    COUNT(*) AS total_clientes,
    SUM(COUNT(*)) OVER (ORDER BY tenure) AS total_acumulado,
    ROUND((SUM(COUNT(*)) OVER (ORDER BY tenure) * 100.0 / SUM(COUNT(*)) OVER())::numeric, 2) AS percentual_acumulado
FROM customers GROUP BY tenure
ORDER BY tenure;

-- Total acumulado de churn por tenure
SELECT
    tenure AS anos_relacionamento,
    SUM(CASE WHEN exited THEN 1 ELSE 0 END) AS churn_no_periodo,
    SUM(SUM(CASE WHEN exited THEN 1 ELSE 0 END)) OVER (ORDER BY tenure) AS churn_acumulado,
    ROUND((SUM(SUM(CASE WHEN exited THEN 1 ELSE 0 END)) OVER (ORDER BY tenure) * 100.0 /
        SUM(SUM(CASE WHEN exited THEN 1 ELSE 0 END)) OVER())::numeric, 2) AS percentual_churn_acumulado
FROM customers GROUP BY tenure
ORDER BY tenure;

-- 5. COMBINANDO CHURN COM WINDOW FUNCTIONS
-- Ranking de países por taxa de churn
SELECT
    geography AS pais,
    COUNT(*)  AS total_clientes,
    SUM(CASE WHEN exited THEN 1 ELSE 0 END) AS total_churn,
    ROUND((SUM(CASE WHEN exited THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS taxa_churn,
    RANK() OVER (ORDER BY SUM(CASE WHEN exited THEN 1 ELSE 0 END) * 1.0 / COUNT(*) DESC) AS ranking_churn
FROM customers GROUP BY geography
ORDER BY ranking_churn;

-- Clientes com saldo acima da média do país e que saíram
SELECT
    customer_id,
    surname,
    geography AS pais,
    balance AS saldo,
    media_saldo_pais,
    exited AS saiu
FROM (
    SELECT
        customer_id,
        surname,
        geography,
        balance,
        exited,
        ROUND(AVG(balance) OVER (PARTITION BY geography)::numeric, 2) AS media_saldo_pais
    FROM customers
) subquery
WHERE exited = true AND balance > media_saldo_pais
ORDER BY geography, balance DESC;
