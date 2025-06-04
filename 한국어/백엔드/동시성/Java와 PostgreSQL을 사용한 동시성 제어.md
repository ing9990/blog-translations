```
original: https://dev.to/ramoncunha/how-to-deal-with-race-conditions-using-java-and-postgresql-4jk6
translator: @ing9990
notes: |
  - 이 글은 원문의 기술적 의도를 최대한 유지하며 번역되었습니다.
```

--- 

## 락을 사용한 데이터베이스 동시성을 제어

상상해보자 당신은 이커머스 시스템을 운영하고 있다. 그리고 천명 이상의 사용자가 마지막 남은 단 한개의 상품을 두고 동시에 구매하려 한다. 그러나 많은 사용자들이 결제와 주문을
완료하였고 재고를 확인했을 땐 상품의 재고가 마이너스 수량이 남았다. 어떻게 이런 일이 발생했을까? 그리고 어떻게 해결할 수 있을까?

시작해보자! 첫 번째로 결제하기 전에 재고를 확인하는 방법을 생각해볼 수 있다.

- 아마 이런 식으로 진행될 것이다.

    ```java
    public void validateANdDecreaseSolution(long productId, int quantity){
    	Optional<StockEntity> stockByProductId = 
            stockRepository.findStockByProductId(productId);
    		
    	int stock = stockByProductId.orElseThrow().getStock();
    	int possibleStock = stock - quantity;
    	
    	if(stock <= 0 || possibleStock < 0){
    		throw new OutOfStockException("Out of stock");
    	}
    	
    	stockRepository.decreaseStock(productId, quantity);
    }
    ```

당신은 위 같은 유효성 검사를 이용할 수 있다. 그러나 초당 수 백만 개의 요청을 다루기 위해서는 위 검증은 부족하다. 10개의 요청이 이 코드에 동시 도달했을 때, 데이터베이스는
`stockByProductId`의 결과로 같은 값을 반환하게 되고, 당신의 코드는 실패한다. 당신은 검증 과정 중에 다른 응답들을 Block할 수 있는 방법이 필요하다.

## 첫 번째 방법 - FOR UPDATE

`SELECT` 절에 `LOCK` 구문을 추가하자. 이 예시에서는 Spring Data에서 `FOR UPDATE`를 사용했다.

- PostgreSQL의 문서에 따르면

    ```text
    FOR UPDATE는 SELECT 문으로 검색된 행을 업데이트용처럼 잠기게 합니다.
    이것은 수정과 삭제를 다른 트랜잭션으로부터 현재 트랜잭션이 종료될때까지 막습니다.
    ```


- 예시 코드

    ```java
    // repo
    @Query(value = "SELECT * FROM stocks s WHERE s.product_id = ?1 FOR UPDATE, nativeQuery = true)
    Optional<StockEntity> findStockByProductIdWithLock(Long productId);
    
    // service
    public void validateAndDecreaseSolution1(long productId, int quantity) {
    	Optional<StockEntity> stockByProductId = stockRepository.findStockByProductIdWithLock(productId);
    	 // ... 검증
        stockRepository.decreaseStock(productId, quantity);
    }
    ```

상품 ID를 사용하여 `stocks` 테이블에 접근하는 모든 요청은 실제 트랜잭션이 종료될 때까지 기다립니다. 이 목적은 마지막으로 수정된 상품의 수량을 보장하는 것입니다.

## 두 번째 방법 - pg_advisotry_xact_lock

이 방법은 이전 내용과 비슷하다, 다만 당신은 `LOCK`에 사용될 키를 선택할 수 있다. 우리는 검증과 재고 감전체가 끝날 때까지 해당 트랜잭션 전체에 `LOCK`을 걸
것입니다.

- 예시 코드

    ```java
    public void acquireLockAndDecreaseSolution2(long productId, int quantity) {
        Query nativeQuery = entityManager.createNativeQuery("select pg_advisory_xact_lock(:lockId)");
        nativeQuery.setParameter("lockId", productId);
        nativeQuery.getSingleResult();
    
        Optional<StockEntity> stockByProductId = stockRepository.findStockByProductId(productId);
    
        // check stock and throws exception if it is necessary
    
        stockRepository.decreaseStock(productId, quantity);
    }
    ```


- **`pg_advisory_xact_lock(:lockId)`**
    - PostgreSQL의 내장 함수로, 지정된 숫자 (예: productId)를 기준으로 트랜잭션에 락을 겁니다.
    - 해당 트랜잭션이 종료될 때까지 같은 `lockId`에 대해 다른 트랜잭션은 대기하게 됨.

같은 상품 ID로 들어온 다음 요청은 이 트랜잭션이 종료되어야 처리됩니다.

## 세 번째 방법 - WHERE 절

이 방법은 행이나 트랜잭션에 락을 걸지 않습니다.   `UPDATE` 구문이 실행되기 전까지는 트랜잭션이 지속되게 둡니다. WHERE의 마지막 조건은 `stock > 0`입니다.
이것은 재고가 0 미만으로 내려가는 것을 허용하지 않습니다. 만약 두 사람이 동시에 요청한다면 데이터베이스가 `stock ≤ -1`을 허용하지 않기 때문에 둘 중 한 사람은 반드시
오류 메세지를 받게됩니다.

- 예시 코드

    ```java
    @Transactional
    @Modifying
    @Query(nativeQuery = true, value = """
    		UPDATE stocks
    		SET stock = stock - :quantity 
    		WHERE product_id = :productId 
    			AND stock > 0
    	"""
    )
    
    int decreaseStockWhereQuantityGreaterThanZero(
    	@Param("productId") Long productId, 
    	@Param("quantity") int quantity
    );
    ```

## 결론

1번과 2번 방법은 비관적 락을 전략으로 사용했습니다. 그리고 세번 째는 낙관적 락을 사용했습니다. 비관적 락 전략은 이 리소스과 관련된 어떤 작업이던 진행될 때 리소스에 제한적인
접근을 위해 사용됩니다. 타겟 리소스는 당신이 작업을 마칠때까지 다른 접근을 막기 위해 락에 걸립니다. 교착 상태를 주의해야 합니다.

낙관적 락과 함께 당신은 Block 없이 여러 쿼리를 만들 수 있습니다. 이것은 트랜잭션 간 충돌이 잘 일어나지 않거나 행과 관련된 version 컬럼을 가져야 합니다. 당신이 이
행을 업데이트하면 데이터베이스는 업데이트한 행의 버전과 데이터베이스의 행 버전을 비교합니다. 만약 두개가 같다면 변경은 성공합니다. 아니라면 재시도를 해야합니다. 보다싶이 이
글에는 버전에 대한 컬럼이 없습니다. 그러나 마지막 방법은 어떤 요청들에 대해서도 Block하지 않으면서 `stock > 0` 조건을 사용해 동시성을 제어합니다.