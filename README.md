<div align="center">
  <br>
  <a href="https://devtuga.herokuapp.com"><img
    alt="DEV"
    src="app/static/Banner.png"
    width=100px
  /></a>
  <h1>DevTuga Notícias 🇵🇹👨🏻‍💻</h1>
  <strong>Um plataforma para hackers que gostam de bitoque.</strong>
</div>

### Índice:

- [Sobre](#sobre)
- [Stack](#stack)
- [Contribuir](#contribuir)
- [Setup](#setup)


### Sobre
Bem vindo ao repositório de código do devTuga news. O devtuga é uma plataforma para hackers portugueses partilharem noticias e discutirem o panorama técnologico actual. 


### Stack
O devtuga usa as seguintes tecnologias: 

- Flask 
- SQL Alchemy
- Docker
- E outras que podes consultar nos [`requirements.txt`](https://github.com/duarteocarmo/devtuga-news/blob/master/requirements.txt)


### Contribuir
Adorávamos que participasses no desenvolvimento e melhoramento do website. 

Podes contribuir de várias formas: 

- Abre uma issue para qualquer bug que encontres ou feature que queiras
- Manda um email para [aqui](mailto:devtuga.2018@gmail.com) no caso de te quereres juntar como contribuidor!

### Setup

- clona este repo

```bash
$ git clone https://github.com/duarteocarmo/devtuga-news
```

- cria um virtual environment
- instala as dependências

```bash
(venv) $ pip install -r requirements.txt
```

- cria um ficheiro `.env` no directorio principal com as seguintes componentes

```python
FLASK_APP=dev.py
SECRET_KEY = "a tua chave secreta"
MAIL_ADMIN_ADDRESS = <email de admin que escolhes tu>
MAIL_SERVER = <servidor de emai ex:smtp.googlemail.com>
MAIL_PORT = <port de email ex:587>
MAIL_USE_TLS = <usar tls? ex:1(sim) ou 0(não)>
MAIL_USERNAME = <email de admin que escolhes tu>
MAIL_PASSWORD = <password do teu email>
```

- inicia a base de dados

```bash
(venv) $ flask db init
(venv) $ flask db upgrade
```

- 🎉Carrega benfica🎉

```bash
(venv) $ flask run
```

- visita [`http://localhost:5000`](http://localhost:5000) para veres o site live na tua maquina.


Feito com muito ☕️ (delta).


