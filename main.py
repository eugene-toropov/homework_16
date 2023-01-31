# Импортируем необходимые методы, библиотеки и т.д.
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json
import data
from _datetime import datetime

# Регистрируем приложение, указываем кодировку, определяем место хранения нашей БД.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """
    Создание класса/модели ДБ User(пользователь).

    Создаем класс и прописываем ему поля:
        Id (идентификационный номер, первичный ключ),
        first_name (имя),
        last_name (фамилия),
        age (возраст),
        email (электронная почта),
        role (должность),
        phone (телефон);
    а также метод to_dict для преобразования данных в словарь.
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(200))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'email': self.email,
            'role': self.role,
            'phone': self.phone
        }


class Order(db.Model):
    """
    Создание класса/модели ДБ Order(заказ).

    Создаем класс и прописываем ему поля:
        Id (идентификационный номер, первичный ключ),
        name (название),
        description (описание),
        start_date (начало выполнения),
        end_date (окончание выполнения),
        address (адрес),
        price (цена),
        customer_id (идентификационный номер, внешний ключ от User.id),
        executor_id (идентификационный номер, внешний ключ от User.id);
    а также метод to_dict для преобразования данных в словарь.
    """
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(200))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'address': self.address,
            'price': self.price,
            'customer_id': self.customer_id,
            'executor_id': self.executor_id
        }


class Offer(db.Model):
    """
    Создание класса/модели ДБ Offer(договор).

    Создаем класс и прописываем ему поля:
        Id (идентификационный номер, первичный ключ),
        order_id (идентификационный номер, внешний ключ от Order.id),
        executor_id (идентификационный номер, внешний ключ от User.id);
    а также метод to_dict для преобразования данных в словарь.
    """
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'executor_id': self.executor_id
        }


with app.app_context():
    """
    Вызываем команду для создания моделей.
    """
    db.create_all()

    for user_ in data.users:
        """
        Из файла data берем данные и, проходя по ним циклом, создаем экземпляры класса User, которые добавляем в БД.
        """
        new_user = User(**user_)
        db.session.add(new_user)

    for order_ in data.orders:
        """
        Из файла data берем данные и, проходя по ним циклом, создаем экземпляры класса Order, которые добавляем в БД.
        Поля start_date и end_date преобразуем в удобный формат для чтения JSON'ом.
            
        """
        order_['start_date'] = datetime.strptime(order_['start_date'], '%m/%d/%Y').date()
        order_['end_date'] = datetime.strptime(order_['end_date'], '%m/%d/%Y').date()
        new_order = Order(**order_)
        db.session.add(new_order)

    for offer_ in data.offers:
        """
        Из файла data берем данные и, проходя по ним циклом, создаем экземпляры класса Offer, которые добавляем в БД.
        """
        new_offer = Offer(**offer_)
        db.session.add(new_offer)

    db.session.commit()  # Подтверждаем действия.


@app.route('/users', methods=['GET', 'POST'])
def users():
    """
    Представление '/users', methods=['GET', 'POST'].

    Возвращает данные согласно проверке операторами 'if/elif'.
    """
    if request.method == 'GET':
        """
        Если выбран метод 'GET', то обращаемся к модели для получения всего списка юзеров, пропущенного через
        'json.dumps'.
        """
        raw_users = User.query.all()
        result = [raw_user.to_dict() for raw_user in raw_users]
        return json.dumps(result)
    elif request.method == 'POST':
        """
        Если выбран метод 'POST', то получаем данные через 'json.loads' и на их основе создаем экземпляр класса
        'User'. Добавляем и подтверждаем.
        """
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return 'Ok'


@app.route('/users/<uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid):
    """
    Представление '/users/<uid>', methods=['GET', 'PUT', 'DELETE'].

    Возвращает данные согласно проверке операторами 'if/elif'.
    """
    if request.method == 'GET':
        """
        Если выбран метод 'GET', то обращаемся к модели по полю класса ID. Полученные данные преобразовываем в словарь
        и пропускаем через 'json/dumps'. 
        """
        user = User.query.get(uid)
        result = user.to_dict()
        return json.dumps(result)
    elif request.method == 'DELETE':
        """
        Если выбран метод 'DELETE', то обращаемся к модели по полю класса ID. Полученный экземпляр удаляем
        и подтверждаем.
        """
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        return 'Ok'
    elif request.method == 'PUT':
        """
        Если выбран метод 'PUT', то сначала получаем данные через 'json/loads', затем экземпляр класса по полученному 
        полю 'id'. После чего экземпляр 'user' обновляем, согласно полученным данным.
        Подтверждаем изменения.
        """
        user_data = json.loads(request.data)
        user = User.query.get(uid)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.add(user)
        db.session.commit()
        return 'Ok'


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    """
    Представление '/orders', methods=['GET', 'POST'].

    :return: Данные согласно проверке операторами 'if/elif'.
    """
    if request.method == 'GET':
        """
        Метод 'GET'. Получает список всех записей 'order' и через цикл 'for' преобразует их в список словарей, 
        предварительно изменив поля 'start_date' и 'end_date'. Возвращает через 'json.dumps.
        """
        raw_orders = Order.query.all()
        result = []
        for raw_order in raw_orders:
            order_dict = raw_order.to_dict()
            order_dict['start_date'] = str(order_dict['start_date'])
            order_dict['end_date'] = str(order_dict['end_date'])
            result.append(order_dict)
        return json.dumps(result)
    elif request.method == 'POST':
        """
        Метод 'POST'. Получает данные из запроса 'request' через 'json.loads(request.data)'.
        На основе этих данных создает экземпляр 'order'(предварительно изменив формат даты)
        Добавляет экземпляр и подтверждает.
        """
        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()

        order = Order(
            name=order_data['name'],
            description=order_data['description'],
            start_date=order_data['start_date'],
            end_date=order_data['end_date'],
            price=order_data['price'],
            customer_id=order_data['customer_id'],
            executor_id=order_data['executor_id']
        )
        db.session.add(order)
        db.session.commit()

        return 'Ok'


@app.route('/orders/<oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid):
    """
    Представление '/orders/<oid>', methods=['GET', 'PUT', 'DELETE'].

    :return: Данные согласно проверке операторами 'if/elif'.
    """
    if request.method == 'GET':
        """
        Метод 'GET'. Получает экземпляр 'order' по 'id'. Преобразует в словарь, изменив формат даты.
        Возвращает через 'json.dumps'.
        """
        result = Order.query.get(oid)
        order = result.to_dict()
        order['start_date'] = str(order['start_date'])
        order['end_date'] = str(order['end_date'])
        return json.dumps(order)
    elif request.method == 'DELETE':
        """
        Метод 'DELETE'. Получает экземпляр 'order' по 'id'. Удаляет его и подтверждает.
        """
        order = Order.query.get(oid)
        db.session.delete(order)
        db.session.commit()
        return 'Ok'
    elif request.method == 'PUT':
        """
        Метод 'PUT'. Получает данные через 'json/loads'. Получает экземпляр 'order' по 'id'. Обновляет
        полученный экземпляр согласно данным. Подтверждает изменения.
        """
        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()

        order = Order.query.get(oid)
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return 'Ok'


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    """
    Представление '/offers', methods=['GET', 'POST'].

    :return: Данные согласно проверке операторами 'if/elif'.
    """
    if request.method == 'GET':
        """
        Метод 'GET'. Получает все экземпляры класса 'Offer'. Преобразует их в список словарей.
        Возвращает через 'json.dumps'.
        """
        raw_offers = Offer.query.all()
        result = [raw_offer.to_dict() for raw_offer in raw_offers]
        return json.dumps(result)
    elif request.method == 'POST':
        """
        Метод 'POST'. Получает данные через 'json.loads' и на их основе создает экземпляр 'offer'.
        Добавляет его и подтверждает.
        """
        offer_data = json.loads(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()
        return 'Ok'


@app.route('/offers/<ofid>', methods=['GET', 'PUT', 'DELETE'])
def offer(ofid):
    """
    Представление '/offers/<ofid>', methods=['GET', 'PUT', 'DELETE'].

    :return: Данные согласно проверке операторами 'if/elif'.
    """
    if request.method == 'GET':
        """
        Метод 'GET'. Получает экземпляр 'offer' по 'id'. Преобразует в словарь.
        Возвращает через 'json.dumps'.
        """
        offer = Offer.query.get(ofid)
        result = offer.to_dict()
        return json.dumps(result)
    elif request.method == 'DELETE':
        """
        Метод 'DELETE'. Получает экземпляр 'offer' по 'id'. Удаляет его и подтверждает.
        """
        offer = Offer.query.get(ofid)
        db.session.delete(offer)
        db.session.commit()
        return 'Ok'
    elif request.method == 'PUT':
        """
        Метод 'PUT'. Получает данные через 'json/loads'. Получает экземпляр 'offer' по 'id'. Обновляет
        полученный экземпляр согласно данным. Подтверждает изменения.
        """
        offer_data = json.loads(request.data)
        offer = Offer.query.get(ofid)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return 'Ok'


# Запускаем приложение.
if __name__ == "__main__":
    app.run()
