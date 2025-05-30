```
original: https://medium.com/@AlexanderObregon/how-to-implement-distributed-transactions-with-the-saga-pattern-using-spring-boot-92924f6d4b23#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6ImJhYTY0ZWZjMTNlZjIzNmJlOTIxZjkyMmUzYTY3Y2M5OTQxNWRiOWIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDg4MjE2Mjk2MzI4NjQ2Mjg2NzIiLCJlbWFpbCI6Im1haWw4MDc4MjI1OEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmJmIjoxNzQ4MzMxNTM2LCJuYW1lIjoi6rmA7YOc7JqwIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0x2R3kyMjJtNzBGY1BDZjJRckxBUU14cS1Ba1FiTmVZWHRibnNnNUdfTmF2OHJBa1BMPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6Iu2DnOyasCIsImZhbWlseV9uYW1lIjoi6rmAIiwiaWF0IjoxNzQ4MzMxODM2LCJleHAiOjE3NDgzMzU0MzYsImp0aSI6IjNjYmVjZWE1YTkxMDhhOTcyMDljMzVkOWRlODFjMDRiY2ZhODYwMTEifQ.H99vHZG_vdR2YcXHbQRJNsRg90TVZKIkbl2oESdwKyZf8b7F-0d_FfL4UVgGpMXhWx-9GdrHi2f_YlvLoiT_XYFe9eY39hupAK4hYVcL2rtwTYmCe3U9wh8R7OPsvw7Di6owyZ5lSYgYtsNdwdUO6o8ZIL6OZ_AZKKnoiLUOiUw_DSIy0wz91er6vo_sH1AnhNh8ifA9X238xJnmwvpCPJIkOB7vA5V25GdUOZ312QU3xaPDKGvg9WrW_WDNm-bz48DCc4GTmQryaN4exrvl0OsP9KBNaPpvY_Z1wNJ7yacSgpykvEWXl0zDseMNPnvxPRETZyvQAIzrGqmxnH2_7w|
translator: @ing9990
notes: |
  - 이 글은 원문의 기술적 의도를 최대한 유지하며 번역되었습니다.
  - 영어 원문을 번역한 것이기 때문에 일부 어색할 수 있습니다.
  - 일부 어색할 수 있거나 중이적으로 들리는 문장은 원문을 Codebox로 첨부하겠습니다.
```

--- 

# Springboot가 Saga 패턴을 사용하여 분산 트랜잭션을 구현하는 방법

번역 기준 단어

| 원문                         | 해석                               |
|----------------------------|----------------------------------|
| Operation                  | 작업 (트랜잭션이 시작되고 완료될때까지 해야 하는 작업들) |
| Event Driven Messaging     | 이벤트 기반 메세징                       |
| Global Transaction Manager | 전체를 아우르는 트랜잭션 매니저                |
| State Tracking             | 상태 추적                            |
| Ochestrator                | 오케스트레이터                          |

## 서론

마이크로서비스 시스템에서는 각 서비스가 각각 데이터베이스를 가지기 때문에, 전통적인 ACID(원자성, 일관성, 격리성, 지속성) 트랜잭션을 여러 서비스에 걸쳐 적용하기 어렵습니다.

스프링부트 어플리케이션은 서비스 간의 트랜잭션을 관리하기 위해 Saga 패턴을 구현하며, 단일 데이터베이스 트랜잭션에 의존하지 않고 서비스의 상태를 일관되게 유지할 수 있도록
합니다.

```
allowing them to stay in sync without relying on a single database transaction.
```

이 글은 어떻게 스프링부트가 내부적으로 Saga Pattern을 활용하여 분산 트랜잭션을 관리하고 있는지 분석합니다. 이를 가능하게 하는 매커니즘에 집중하여 설명합니다.

## 분산 트랜잭션과 Saga Pattern

마이크로 시스템에서, 비즈니스 작업은 각각의 데이터베이스를 가지는 여러 서비스를 아우릅니다.

이것은 하나의 데이터베이스 트랜잭션으로 모든 것을 일관성을 유지하는 모놀리식 어플리케이션에 비해 트랜잭션을 다루는 것을 더욱 복잡하게 만듭니다.

전통적인 ACID 트랜잭션은 단일 데이터베이스에 의존하거나, 2PC 같은 분산 트랜잭션 프로토콜에 의존합니다. 이 방법은 병목현상과 서비스들이 단단한 결합 때문에마이크로서비스에서는
잘 작동하지 않습니다.

**Blocking 하거나 확장성을 제한하는 의존성을 만들지 않고 여러 데이터베이스에 걸쳐 트랜잭션을 적용하기 위해 Saga Pattern이 쓰입니다.**

작업을 하나의 큰 트랜잭션으로 취급하는 대신 Saga는 작은 스텝으로 쪼갭니다.

각 서비스는 독립적으로 완수하고, 다음 스텝을 호출합니다. 만약 무엇이던 잘못되면 보상 트랜잭션이 이전 작업을 취소하여 비일관성을 방지합니다.

## 왜 마이크로서비스에서  ACID 트랜잭션이  동작하지 않는가?

ACID 트랜잭션은 모든 작업이 같은 데이터베이스에서 일어나는 상황을 위해 디자인되었습니다.

마이크로 서비스에서는 각 서비스가 독립된 데이터베이스와 독립된 네트워크에서 통신하고 이것은 몇몇 문제를 발생시킵니다.

- 공유되지 않는 트랜잭션 매니저

  모놀리식 시스템에서는 모든 스텝이 모두 성공하거나 뭔가 잘못된 경우엔 롤백되는 것을 데이터베이스 트랜잭션 매니저가 보장합니다. 마이크로 서비스는 중앙 트랜잭션 매니저가
  없습니다, 즉 실패가 발생했을 때 모든 변경을 취소하는 기능이 구비되어 있지 않습니다.

- 네트워크 지연과 실패

  분산 트랜잭션은 여러 서비스의 신뢰성 있는 통신에 의존합니다.

  네트워크 실패나 서비스 충돌은 프로세스를 중단시키고, 몇몇 변경들은 다른 영속 상태와 불일치 되는 상태로 남겨질 수 있습니다.


- Two-Phase Commit(2PC) 문제

  일부 시스템은 모든 서비스가 성공을 확인할 때까지 리소스에 Lock을 건 뒤, 변경 사항을 커밋하기 위해 2PC를 사용합니다. 이 작업은 트랜잭션을 느리게 하고, 데이터베이스의
  락을 발생시켜 다른 작업들이 방해받을 수 있습니다.

이런 어려움 때문에 기존 마이크로 서비스에 걸쳐 데이터베이스 트랜잭션을 의존하는 것은 실용적이지 않습니다. 이것이 다른 방법이 필요한 이유입니다.

## 어떻게 Saga Pattern이 문제를 해결하는가?

Saga 패턴은 큰 단일 트랜잭션을 작은 일련의 트랜잭션으로 쪼갭니다. 각 단계는 성공적으로 완료하거나 이전 변경사항을 취소하기 위해서 **보상 액션**을 호출합니다. 전체를
아우르는 트랜잭션 매니저를 사용하기보다 서비스들은 이벤트를 통해 통신하며 각자의 트랜잭션을 다룹니다.

### Saga 를 구현하기 위한 2가지의 일반적인  방법

- **이벤트 기반 (Choreography-Based Saga)**

  각 서비스는 이벤트를 감지하고, 필요에 따라 응답합니다. 한 서비스가 하나의 스텝을 완료하면 다음 서비스가 받을 이벤트를 발행합니다. 만약 작업이 실패했다면 `Rollback`
  이벤트가 발행됩니다. 그리고 이전 서비스는 변경 사항을 되돌립니다.

- **오케스트레이션 기반 (Orchestration-Based Saga)**

  중앙 오케스트레이터 트랜잭션 흐름을 제어합니다. 서비스들의 직접적인 통신 대신 서비스들은 오케스트레이터로부터 내려오는 메세지를 기다립니다. 만약 오류가 발생하면 오케스트레이터는
  필요한 보상 액션을 결정합니다.

두 방법 모두 전체를 아우르는 트랜잭션 매니저가 필요하지 않습니다. 또한 데이터를 일관성있게 유지하면서도 서비스들이 느슨하게 결합하도록 유지합니다.

## 어떻게 스프링 부트가 내부적으로 Saga Pattern 구현하는가?

스프링부트는 사가 패턴을 활용한 분산 트랜잭션을 다루는 방법을 여러 방법으로 제공합니다.

내부적으로 **이벤트 기반 통신과 메세지 브로커(MQ), 그리고 상태 관리를** 수반합니다.

스프링 부트가 이러한 트랜잭션을 조정하는 방법은 시스템이 **Choreography Based인지 Orchestration Based**인지에 따라 다릅니다.

### Choreograpy 기반 Saga 패턴

스프링 부트 어플리케이션은 마이크로서비스에 걸친 트랜잭션을 다루기 위해 이벤트 기반 아키텍처에 의존합니다. 서비스 간의 직접적인 호출 대신, 이벤트는 다른 액션들의 트리거를
유발하는 신호의 역할을 합니다.

이러한 방식은 서비스에 임시적으로 장애가 발생해도 트랜잭션이 지속적으로 동작할 수 있게 만듭니다.

1. A 서비스가 트랜잭션을 시작하고, 메세지 브로커(`Kafka`, `RabbitMQ`, `ActiveMQ`)에게 메세지를 발행합니다.
2. 다른 서비스들은 이벤트와 연관된 서비스를 구독하고, 비동기적으로 진행시킵니다.
3. 만약 작업이 실패하면 이전 변경들을 되돌리는 **보상 트랜잭션**이 발행됩니다.

스프링 부트 어플리케이션들은 주로 서비스들이 **메세지 브로커와 결합하고 내부적 디테일을 알 필요 없이 메세지를 전송하거나 받을 수 있도록** 하면서도 각 서비스는 언제 액션을
취해야 하는지 알 수 있게 하는 **`Spring Cloud Stream`**을 사용합니다.

이벤트를 발행하기 전에 그 구조를 정의하는 클래스가 필요합니다.

`OrderCreatedEvent` 는 주문에 대한 핵심 정보를 가집니다.

- 주문 ID
- 수량
- 상품 ID

또한 이 이벤트는 마이크로 서비스들에 전파되며 트랜잭션 과정을 조율하는데 사용됩니다.

```java
public class OrderCreatedEvent {

    private final String orderId;
    private final BigDecimal amount;
    private final String itemId;

    // getters and constructors
}
```

이제 이벤트 정의가 끝났습니다. 우리는 이 주문이 생성되었을 때 이벤트를 전송하는 이벤트 발행자(Event Publisher)를 구현해야 합니다.

- 이벤트를 발행하는 서비스의 예시

    ```java
    @Component
    public class OrderEventPublisher {
    
        private final StreamBridge streamBridge;
    
        public OrderEventPublisher(StreamBridge streamBridge) {
            this.streamBridge = streamBridge;
        }
    
        public void publishOrderCreatedEvent(String orderId, BigDecimal amount, String itemId) {
            OrderCreatedEvent event = new OrderCreatedEvent(orderId, amount, itemId);
            streamBridge.send("orderCreated-out-0", MessageBuilder
                .withPayload(event)
                .setHeader(MessageHeaders.CONTENT_TYPE, MimeTypeUtils.APPLICATION_JSON)
                .build());
        }
    }
    ```


- 이벤트를 구독하는 다른 서비스의 예시

    ```java
    @Component
    public class PaymentEventListener {
    
        @Bean
        public Consumer<OrderCreatedEvent> handleOrderCreatedEvent() {
            return event -> processPayment(event.getOrderId());
        }
    
        private void processPayment(String orderId) {
            // Payment processing logic goes here
        }
    }
    ```

이런 구성에서는 각 서비스가 독립적으로 동작하며, 자신과 관련된 이벤트만을 구독합니다.

각자 직접 호출하는 방식 대신에 브로커를 통한 메세지에 반응합니다. 이것은 트랜잭션이 **누가 다음 스텝을 처리하는지 알 필요가 없으면서도 다음 단계를 진행**할 수 있습니다.

- Saga 오케스트레이터가 동작하는 방법

  오케스트레이션 기반 Saga는 중앙 Coordinator가 전체 트랜잭션을 조율합니다. 이것은 다른 서비스에게 명령을 보내고, 각 서비스가 응답하기를 기다립니다. 그리고 그들의
  응답에서 다음에 무슨 일을 할지 결정합니다. 이것은 모든 것들을 체계적으로 유지하고 시스템에 문제가 생겼을 때 대응할 수 있도록합니다.

  스프링부트 어플리케이션은 이 방법을 구현하기 위해 `Axon Framework` 를 사용합니다.

  `Axon` 은 분산 트랜잭션을 이벤트와 커맨드를 사용하여 다루는 도구를 제공합니다. 오케스트레이터는 어떤 스텝이 완료되었는지, 혹은 실패했는지, 오류 발생 시 이전 변경
  사항에 대해 보상 트랜잭션이 작동하였는지 추적합니다.

### Saga 오케스트레이터의 예시

```java

@Saga
public class OrderSaga {

    @Autowired
    private transient CommandGateway commandGateway;


    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCreatedEvent event) {
        String paymentId = UUID.randomUUID().toString();
        ProcessPaymentCommand command = new ProcessPaymentCommand(paymentId, event);
        commandGateway.send(command);
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentProcessedEvent event) {
        ReserveInventoryCommand command = new ReserveInventoryCommand(event.getOrderId(),
            event.getItemId());
        commandGateway.send(command);
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentFailedEvent event) {
        CancelOrderCommand command = new CancelOrderCommand(event.getOrderId());
        commandGateway.send(command);
        end();
    }
}
```

`OrderSaga` 클래스는 분산 트랜잭션을 Command를 다른 마이크로 서비스에게 보냄으로써 조율합니다.

이것이 발행한 주요 Command중 하나는 결제 프로세스를 시작하기 위해 `PaymentService`에 발송된 `ProcessPaymentCommand`입니다.

이 Command가 `OrderSaga`에 의해 사용되기 때문에, 필요한 결제 정보들을 담기위해 이것을 분리된 클래스로 정의해야 합니다.

아래는 결제 서비스에 전달될 결제와 관련된 정보를 가지는 `ProcessPaymentCommand`의 정의입니다.

```java
public class ProcessPaymentCommand {

    private final String paymentId;
    private final String orderId;
    private final BigDecimal amount;
    private final String itemId;
    // getters and constructors
}
```

`ProcessPaymentCommand`이 결제 요청을 시작하는 책임을 갖는 한편, 실패에 대한 처리 방법 또한 존재해야 합니다. 만약 결제 시도가 성공하지 못했다면, 시스템은
마이크로 서비스 간의 일관성을 유지하기 위해 롤백 액션이 실행되어야 합니다.

`PaymentFailedEvent` 는 결제가 진행되지 않으면 발행되고, Saga 오케스트레이터에게 주문을 취소하거나 관련된 트랜잭션을 되돌리는 것같은 올바른 액션을 취하도록
알립니다.

아래는 실패 시 정보들을 담고 있는 `PaymentFailedEvent` 입니다.

```java
public class PaymentFailedEvent {

    private final String paymentId;
    private final String orderId;
    private final String itemId;
    private final String reason;

    // getters, constructor
}
```

`PaymentFailedEvent` 가 결제 진행 중 실패를 나타내는 한편, 결제가 성공적으로 완료되었을 때를 나타내는 방법도 필요합니다. 여기서
`PaymentProcessedEvent` 를 사용합니다. 결제가 성공적으로 완료되면 이 이벤트가 진행할 다음 스텝에 알리기 위해 발행됩니다.

- 재고를 확보하는 서비스
- 주문 이행

```java
public class PaymentProcessedEvent {

    private final String paymentId;
    private final String orderId;
    private final String itemId;

    public PaymentProcessedEvent(String paymentId, String orderId, String itemId) {
        this.paymentId = paymentId;
        this.orderId = orderId;
        this.itemId = itemId;
    }

    // getters, constructors
}
```

`OrderSaga` 클래스는 서비스 간 트랜잭션을 조율합니다. `@Saga` 어노테이션이 이 클래스를 오케스트레이터로 지정합니다. 이는 이벤트를 수신하고 일련의 트랜잭션 단계를
제어하는 것을 의미합니다.

주문이 만들어지면 `handle(OrderCreatedEvent event)` 메서드가 시작됩니다. 이 메서드는 `ProcessPaymentCommand`를 결제 서비스로 보내
결제를 진행시킵니다.

결제가 성공적이라면 `ReserveInventoryCommand`를 재고 서비스로 보내고 주문을 위한 재고를 예약하기 위해
`handle(PaymentProcessedEvent event)` 메서드가 실행됩니다.

결제 실패 시 `handle(PaymentFailedEvent event)` 메서드가 대신 실행됩니다. 이것은 이전 변경 사항들을 롤백하고 트랜잭션이 end() 메서드를 호출함으로
써 표시합니다.  `CancelOrderCommand`를 전송합니다.

만약 실패가 발생하면 오케스트레이터는 또한 비즈니스 로직에 따라 롤백 이전 Retry 매커니즘을 시도합니다.

스프링부트 어플리케이션은 또한 State Machines를 트랜잭션 추적에 사용합니다.  `Spring Statemachine` 은 트랜잭션 다음 단계로 넘어가기 전 각 단계가
완료되도록 Workflow들을 정의할 수 있는 도구를 제공합니다.

### 예시 - (주문, 결제, 재고) 마이크로 서비스

이것이 실제로 어떻게 작동하는지 확인하려면, 세 개의 마이크로서비스가 트랜잭션의 서로 다른 부분을 처리하는 주문 처리 시스템을 예로 들어보겠습니다.

1. 주문 서비스가 새로운 주문을 만들면서 처리를 시작합니다.
2. 그럼 결제 서비스가 결제를 처리하고, 성공 혹은 실패를 확인합니다.
3. 재고 서비스가 재고 가용성을 확인하고 결제가 성공했다면 아이템을 예약합니다.

만약 결제 시스템이 실패했다면 주문을 취소하기 위해 Saga 오케스트레이터가 `Rollback Command`를 보냅니다. 만약 재고 서비스가 재고를 예약하지 못했다면, 환불을
위해 결제 서비스로 보상 액션이 실행됩니다.

- 주문 서비스

    ```java
    @Aggregate
    public class OrderAggregate {
    
        @AggregateIdentifier
        private String orderId;
        // default constructor
    
        @CommandHandler
        public OrderAggregate(CreateOrderCommand command) {
            apply(new OrderCreatedEvent(command.getOrderId(), command.getAmount(), command.getItemId()));
        }
    }
    ```

  주문 서비스는 새로운 주문을 생성함으로써 트랜잭션을 시작합니다. 주문 요청이 들어오면 `CreateOrderCommand` 가 주문의 상태를 추적하는
  `OrderAggregate` 생성을 시작합니다.

  `apply()` 메서드는 서비스들에게 주문이 생성됨을 알리기 위해 `OrderCreatedEvent`를 만들어 보냅니다. 이 시점에 트랜잭션은 완료되지 않습니다. 주문이
  완전히 완료되기 전까지 체인에 있는 다음 서비스들 역시 자기 역할을 수행해야 합니다.

- 결제 서비스

    ```java
    @Aggregate
    public class PaymentAggregate {
    
        @AggregateIdentifier
        private String paymentId;
    
        // default constructor 
    
        @CommandHandler
        public PaymentAggregate(ProcessPaymentCommand command) {
            this.paymentId = command.getPaymentId();
            
            if (command.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
                apply(new PaymentFailedEvent(
                    command.getPaymentId(),
                    command.getOrderId(),
                    command.getItemId(),
                    "Payment amount must be greater than zero"
                ));
            } else {
                apply(new PaymentProcessedEvent(
                    command.getPaymentId(),
                    command.getOrderId(),
                    command.getItemId()
                ));
            }
        }
    }
    ```

  Saga는 `OrderCreatedEvent` 을 수신하고 결제 서비스에 `ProcessPaymentCommand`를 보냄으로 결제 단계를 시작합니다. 결제 서비스가 이
  커맨드를 받으면, 먼저 수량이 정확한지 검증합니다. 만약 재고가 1보다 작다면 트랜잭션은 즉시 실패합니다. 그렇지 않은 경우 프로세스는 다음 단계로 진행되며
  `PaymentProcessedEvent`를 발생시켜 결제가 완료되었음을 다음 서비스에 전달합니다.

  이후에 만약 결제 처리에 문제가 생긴다면 주문을 취소하기 위해 보상 이벤트가 실행됩니다.

- 재고 서비스

    ```java
    @Aggregate
    public class InventoryAggregate {
    
        @AggregateIdentifier
        private String itemId;
        
        // default constructor
    
        @CommandHandler
        public InventoryAggregate(ReserveInventoryCommand command) {
            this.itemId = command.getItemId();
            apply(new InventoryReservedEvent(command.getOrderId(), command.getItemId()));
        }
    }
    ```

재고 서비스는 주문 아이템을 예약하기 전에 결제가 완료되었는지 확인을 기다립니다.

`ReserveInventoryCommand` 를 수신하면, 재고의 가용성을 확인하고 요청된 아이템을 예약합니다.

재고가 충분하다면, 주문이 계속 진행될 수 있도록 `InventoryReservedEvent` 를 적용합니다.

만약 재고가 없거나 다른 문제가 발생하면 결제 서비스에 환불을 요청하고 주문 서비스에 주문 취소하기 위해 롤백 이벤트가 실행됩니다. 이 작업은 스프링부트가 여러 서비스에 걸친
트랜잭션을 서로를 직접 호출하지 않고 다룹니다. 오케스트레이터는 트랜잭션 스텝을 관리합니다. 지속적으로 어떤 단계가 완료되었는지와 문제가 발생한 경우 롤백 액션을 실행합니다.

Event-driven messaging, state tracking, 그리고 command processing은 스프링 부트가 전체를 관리하는 트랜잭션 매니저 없이도 트랜잭션을
다룰 수 있게 합니다. 이것은 복잡한 작업을 조유하며 서비스를 독립적으로 유지하게합니다.

## 결론

스프링 부트는 큰 작업을 서비스를 독립적으로 완료하는 작은 스텝으로 나누는 Saga Pattern을 활용하여 분산 트랜잭션을 다룹니다. 전체를 아우르는 트랜잭션 매니저에 의존하는
대신에 트랜잭션들은 구조적인 트랜잭션 흐름에 서비스들의 결합을 느슨하게 유지하는 이벤트 기반 메세징과 상태 추적에 관리됩니다.

`Axon` 그리고 `Spring Statemachine`같은 도구같은 이벤트 기반 통신, 오케스트레이션 프레임워크는 어플리케이션이 트랜잭션 처리를 추적할 수 있고. 보상 액션이
언제 필요한지 그리고 다른 서비스를 블로킹 하지 않고 실패를 다룰수 있게 돕습니다

이것은 트랜잭션들이 시스템을 확장성 있고 유연하게 유지하면서도 여러 마이크로 서비스에 걸쳐 일관성 있게 유지됩니다.

## 참조

1. [*Spring Boot Documentation*](https://docs.spring.io/spring-boot/docs/current/reference/html/)
2. [*Spring Cloud Stream*](https://docs.spring.io/spring-cloud-stream/docs/current/reference/html/)
3. [*Axon Framework*](https://www.axoniq.io/products/axon-framework)
4. [*Spring Statemachine*](https://docs.spring.io/spring-statemachine/docs/current/reference/html/)