"""Public user API unit tests."""
import json
import pytest
from web3.auto import w3
from eth_account.messages import defunct_hash_message

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.models.user import User
from dapp_store_backend.enums.status import HTTPCodes

user_public_address = '0xef7e0f9A83f83988f4bDeFE115082E1FE42b7ee1'
user_private_key = '0aa4f74555fc028089654ce844fec83c65a60dfabaf41922ebec8da3450ab4a2'


@pytest.mark.usefixtures('session')
def test_get_user_and_nonce(session):
    """
    Test get user associated with address.
    :param session:
    :return:
    """

    client = session.app.test_client()

    payload = {
        'public_address': user_public_address,
    }

    response = client.post('/api/v1/public/user/login',
                           data=json.dumps(payload),
                           follow_redirects=True,
                           content_type='application/json')

    retrieved = User.query.filter(User.address == user_public_address).first()
    assert response.status_code == HTTPCodes.Success.value
    assert retrieved.address == user_public_address
    assert retrieved.username == user_public_address
    assert retrieved.email is None
    assert retrieved.profile_picture is None
    assert retrieved.blockchain_id == 1
    assert retrieved.s3_id is not None
    assert retrieved.created_at is not None
    assert retrieved.nonce is not None


@pytest.mark.usefixtures('session')
def test_get_user_invalid_eth_address_fail(session):
    """
    Test invalid eth address.
    Outcome: 404 thrown.
    :param session:
    :return:
    """

    client = session.app.test_client()

    payload = {
        'public_address': '0xed081EA02CA571E61309F163226ABe4A4685684d',
    }

    response = client.post('/api/v1/public/user/login',
                           data=json.dumps(payload),
                           follow_redirects=True,
                           content_type='application/json')

    retrieved = User.query.filter(User.address == '0xed081EA02CA571E61309F163226ABe4A4685684d').first()
    assert response.status_code == HTTPCodes.Not_Found.value
    assert retrieved is None


@pytest.mark.usefixtures('session')
def test_authorize_user(session):
    """
    Test authorize user.
    :param session:
    :return:
    """

    client = session.app.test_client()

    payload = {
        'public_address': user_public_address,
    }

    login_response = client.post('/api/v1/public/user/login',
                                 data=json.dumps(payload),
                                 follow_redirects=True,
                                 content_type='application/json')

    assert login_response.status_code == HTTPCodes.Success.value

    added_user = User.query.filter(User.address == user_public_address).first()

    message = 'Logging in as: {username}, nonce: {nonce}'.format(username=added_user.username, nonce=added_user.nonce)
    message_hash = defunct_hash_message(text=message)
    signed_message = w3.eth.account.signHash(message_hash, private_key=user_private_key)

    payload = {
        'public_address': user_public_address,
        'signature': signed_message.get('signature').hex()
    }

    authorize_response = client.post('/api/v1/public/user/authorize',
                                     data=json.dumps(payload),
                                     follow_redirects=True,
                                     content_type='application/json')

    returned_user = authorize_response.get_json()

    assert authorize_response.status_code == HTTPCodes.Success.value
    assert returned_user.get('address') == user_public_address
    assert returned_user.get('username') == user_public_address
    assert returned_user.get('nonce') == added_user.nonce
    assert returned_user.get('token') is not None


@pytest.mark.usefixtures('session')
def test_update_user_no_change(session):
    """
    Test update user endpoint with no change.
    :param session:
    :return:
    """

    client = session.app.test_client()

    payload = {
        'public_address': user_public_address,
    }

    login_response = client.post('/api/v1/public/user/login',
                                 data=json.dumps(payload),
                                 follow_redirects=True,
                                 content_type='application/json')

    assert login_response.status_code == HTTPCodes.Success.value

    added_user = User.query.filter(User.address == user_public_address).first()

    message = 'Logging in as: {username}, nonce: {nonce}'.format(username=added_user.username, nonce=added_user.nonce)
    message_hash = defunct_hash_message(text=message)
    signed_message = w3.eth.account.signHash(message_hash, private_key=user_private_key)

    payload = {
        'public_address': user_public_address,
        'signature': signed_message.get('signature').hex()
    }

    authorize_response = client.post('/api/v1/public/user/authorize',
                                     data=json.dumps(payload),
                                     follow_redirects=True,
                                     content_type='application/json')

    returned_user = authorize_response.get_json()
    token = returned_user.get('token')
    initial_user_address = returned_user.get('address')

    assert authorize_response.status_code == HTTPCodes.Success.value
    assert initial_user_address == user_public_address
    assert returned_user.get('username') == user_public_address
    assert returned_user.get('nonce') == added_user.nonce
    assert token is not None

    payload = {}

    update_response = client.post('/api/v1/public/user/update',
                                  data=json.dumps(payload),
                                  headers={
                                      'Authorization': f'Bearer {token}'
                                  },
                                  follow_redirects=True,
                                  content_type='application/json')

    updated_user = update_response.get_json()

    assert update_response.status_code == HTTPCodes.Success.value
    assert updated_user.get('address') == initial_user_address
    assert updated_user.get('username') == initial_user_address
    assert updated_user.get('profile_picture_url') == ''


@pytest.mark.usefixtures('session')
def test_update_user_username(session):
    """
    Test update username for a user.
    :param session:
    :return:
    """

    client = session.app.test_client()

    payload = {
        'public_address': user_public_address,
    }

    login_response = client.post('/api/v1/public/user/login',
                                 data=json.dumps(payload),
                                 follow_redirects=True,
                                 content_type='application/json')

    assert login_response.status_code == HTTPCodes.Success.value

    added_user = User.query.filter(User.address == user_public_address).first()

    message = 'Logging in as: {username}, nonce: {nonce}'.format(username=added_user.username, nonce=added_user.nonce)
    message_hash = defunct_hash_message(text=message)
    signed_message = w3.eth.account.signHash(message_hash, private_key=user_private_key)

    payload = {
        'public_address': user_public_address,
        'signature': signed_message.get('signature').hex()
    }

    authorize_response = client.post('/api/v1/public/user/authorize',
                                     data=json.dumps(payload),
                                     follow_redirects=True,
                                     content_type='application/json')

    returned_user = authorize_response.get_json()
    token = returned_user.get('token')
    initial_user_address = returned_user.get('address')

    assert authorize_response.status_code == HTTPCodes.Success.value
    assert initial_user_address == user_public_address
    assert returned_user.get('username') == user_public_address
    assert returned_user.get('nonce') == added_user.nonce
    assert token is not None

    new_username = 'IamTheCoolestGuyEver'
    payload = {
        'username': new_username
    }

    update_response = client.post('/api/v1/public/user/update',
                                  data=json.dumps(payload),
                                  headers={
                                      'Authorization': f'Bearer {token}'
                                  },
                                  follow_redirects=True,
                                  content_type='application/json')

    updated_user = update_response.get_json()

    assert update_response.status_code == HTTPCodes.Success.value
    assert updated_user.get('address') == initial_user_address
    assert updated_user.get('username') == new_username
    assert updated_user.get('profile_picture_url') == ''


@pytest.mark.usefixtures('session')
def test_update_user_profile_picture(session):
    """
    Test update profile picture for a user.
    :param session:
    :return:
    """

    client = session.app.test_client()

    payload = {
        'public_address': user_public_address,
    }

    login_response = client.post('/api/v1/public/user/login',
                                 data=json.dumps(payload),
                                 follow_redirects=True,
                                 content_type='application/json')

    assert login_response.status_code == HTTPCodes.Success.value

    added_user = User.query.filter(User.address == user_public_address).first()

    message = 'Logging in as: {username}, nonce: {nonce}'.format(username=added_user.username, nonce=added_user.nonce)
    message_hash = defunct_hash_message(text=message)
    signed_message = w3.eth.account.signHash(message_hash, private_key=user_private_key)

    payload = {
        'public_address': user_public_address,
        'signature': signed_message.get('signature').hex()
    }

    authorize_response = client.post('/api/v1/public/user/authorize',
                                     data=json.dumps(payload),
                                     follow_redirects=True,
                                     content_type='application/json')

    returned_user = authorize_response.get_json()
    token = returned_user.get('token')
    initial_user_address = returned_user.get('address')

    assert authorize_response.status_code == HTTPCodes.Success.value
    assert initial_user_address == user_public_address
    assert returned_user.get('username') == user_public_address
    assert returned_user.get('nonce') == added_user.nonce
    assert token is not None

    payload = {
        'profile_picture': {
            'image': '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBAUEBAYFBQUGBgYHCQ4JCQgICRINDQoOFRIWFhUSFBQXGiEcFxgfGRQUHScdHyIjJSUlFhwpLCgkKyEkJST/2wBDAQYGBgkICREJCREkGBQYJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCT/wAARCAFoAoADASIAAhEBAxEB/8QAHAAAAQQDAQAAAAAAAAAAAAAABAIDBQYAAQcI/8QASRAAAgEDAgQEBAQEBAMGBQMFAQIDAAQRBSEGEjFBEyJRYQcUMnEjQoGRFVKh0QgzYsFDseEWJCVTcvA0RGNzghh0khcmVGTx/8QAGgEAAgMBAQAAAAAAAAAAAAAAAgMAAQQFBv/EACwRAAIDAAICAgICAgEEAwAAAAABAgMRBBIhMRNBBVEUIjJhMwYjQnEVgbH/2gAMAwEAAhEDEQA/AJuObksNPOM4g5etBmcnPbFLeXGn2Of/ACfWome6ZGYlq8fVW9PRSniCWuY+YgnGK2l2ufqqEe9HO2WpUVyrNsa2/A0hKs30WOC8DtjO9SEMh2PrVfsnGQ2d6mLWUHY9ax2wwbFk3atjP/Kj7U1FWrbVJW+M4zXOsi9GaSUbYoqNutAoTmiI260jMCDFbrvTqv1oNGxmn1Of1pZYQOlKpCtkUsb53q0ijdZW9vWs29aIgmtVusqizWKyt5rM1RDK3jIxWUgE1eFG6yt1lUQ1itgda0N6UO9UkWYBgVlZWURDWK1SqTQlGYrdapW3pV4yzQGazFbzisU5q+pRqtVvBrAvXzDI/wCVUk2VuGUpelIxzAsnmUd+lbVl5BIG8h6H/pV9JfondGya1WEhWKMTz/ygb1hVhjmGM9u9RRb9ommVlJ58HpWwc/ep1ZEYWx96z1rFIPbNbx1qvKZfs3ikZpWazA9amkE5rQ3pWKxBQ9iG63jNaxWKcVWlmsVqt5rWatlGgdqwVvFZy+9V4LN4PpWu1brXamIggk9zW87Vo1rtQvyQSBW8e9YNh0NaOaBIhmK1SqTTCCSaQTSyKbIqE01k4reK1yknpSl2ql/svRGPak8op3I9KTUKB3XehZ1GKNcUJcL5agUCOlGT0qNnXJYYxUrIuSx9Kjp9+an1oqSIi6jXzZFQF9ESDt1qy3K5zULdRkk+1dLjPBUipajGSQQKh2jJlJq03VvksDUa1oA+cV3ePLImG2IBb25HNipizgChdqbgthvgVJ2sGfb9KuyQuMTcUOd+1EgYjO1OpCTsBtT4tgY22rFZIdCI4z8umWWT/wAH1qDv5eUt5sVINJmwswfywioLUnzk03i1efJLZeCNnvCZCA1FWM7AeY1DXH1gqN6Jtpj0PWunKlNGSuzGW2znypwamrW4yAR1FVOxnwetTtlJjcGuTyKcNlU9ZabW42qSt36HNQFrMeWpa3k2xXIsiaUyZik5u9FRtmoy2f3oyF81ikhoahyaeQ9BQ8R2Bp9etIZY+h2pxWOTTKHankIzRRB0c3x1rWTWs7Vs0WFmZrdJrdBhZusAzW8VsLirxkNVrApWKSBmiwhlZWGsFBhQpRWcvvWCsqYWjKysHm9qwbj0qyhOa3Wq2AWzgdOtCvfgjMxWUtELeYKeQdXIwKir/irQNKt5prrVoZOQeZImyynft+lbqeJbb/jETO5RJE79KU0bIhdgVjAyHYYUj71yLib493Ef4HCemJJKjgO9wuVP9KoWtfE3WtTnkj1TU7rkchnhtmwsD+ldXj/g5S/5PBlnzUvR6OutX0qxtTcXupWyx5A8jZqnaj8auDNMhlc3U0nhHBYLjmHtXn9tWtb698O+/iD22QXl35f+dNNxFaSu8UNnHHZQSYjM67uPXHpXSr/C1RES5bfo7hN8e7C553stCZ41HMom8rOPUCoO4+O+rtp90trpNsJcZWWE5KD7Y3ri9y2o6tNPfW0kktp9Cs5CnP8Ap9qD0q9TSWWOGSSRmOCg281bIfj64fQr+RL6Z2zQPj5rj6PPLqiW0UsKE8x/zG/TG1C6H/iJ1a1smk1fSZJ3LcyvGu+PtiuZXlzM0UIt7eIyMSLoY8x+xqT0TiC107TDpV0phmV8q7fV+1E+HX+gf5Ev2dStv8Uegkj5vT7mEnu0dWGy/wAQHA2ovyPdCNu+dv29a47BaWMjPciK1vOWPy27p5gP96jJpLGzRkXhyzUg7s655KW/xtL/APEKPIkepNM4w4a1YD5bWLbcZwTg/tUugEq80bq6ncFTnI9a8YPexR3MgS3mheJcrJGSBy+v/SpK0+JvFXCEUV1pmrLdWj7Msm7J7ddqw2/hYP8AxHw5eez13uFyQRnpmtc23v6VwnhH/FDaXBWHiG3aFT1kUcwrsmhcUaDxRGs2l30bFhkAtu32FcTk/jLqnqWo118qMiUrFGK1y+CuREx+5zitg5rmuuSeND00/Juk5pVaoeoeiazFZW8UBDVbzWYrKJIhukkUqtE7VfosbNarZrVVhRrm+/71sjNa5DSk3zVJfosTWq2+1IzjNQhlawK1zVmavCjAMUk7DNLrRGRjNTCxvNazWMKyqwvwNscimJftRBG1NSCiitIngBKp3wOtRtxEwJ2qXljyOlBTx+YitFUfJTZCTJuajLqPIO3Wp24hOWqOuIsjpvXUpQqTK7cxZJGKE+XU/lqakgyzZ2poW4bt/SujW0kZWRiWwXJAH7UfDBlR0FEJajaiILQgjvVzkUkIitmK+maJS15Y2zin0gYYp8RHwmyKxTkNiincxNpa5/8AKAqFvz5celSfPm0td/8Ah1FXhzzGuzTXjMVk0yGYlnalJlTnG9OLH5icU6kJboK1teDMF2btkb1YbGTK4zvUBaRMrjNTdiy4zjeuZyEa6Sx2h96lbd8PUJbSD1qTtnyc5rjWxN6ZMRPgHFGWzb9ajLZs5BO9FwSeasFkcHIlkcZG9Exn3qNjcHv0o2J8isrRAtenWlhqFSSnA/SrisKwI5/elI1Ch8e9LWTNW/8ARYSWranNDq+aWrVEiD+aznpnxK34lEDrHOfNYr9aaMmPetK1Uyax7INKA6702JKUrDfehSCFjpWZxmkK2axpATjpmmximApMUD19qwkAU2ZByEdz6ULqurWGhWhu9SmSMKTiPm3b7+lNo4k7p5BeAZ2KPthyAOFbPLGfztsAarHEvxD0fhlTCyfOXa+V40/y1/WuUcbfGTVOK7uTQOD43n3w9yBiOL+9UjiPSdfjtTZFXaOQAeOX3kNek4n4mMPMkc6zlOXou3GPxc1biAi2sJ5Qqt+IINljHua57Dw/qMmqymfWljS6HNJ+JzEjfYfvQbpqHD8a2elhriQoVueU5LsMdv1qCXXmhuPFlt3jlQYctuB7CuvGhR9GWU2y4a9xjLYk2VpYGWzChHkK4L++e1BycT2dpbt8ppwldmDyErufcGq62q3d9cmKQtJakfQopyOSWLltIopIuT/Kdxsy+9PUUhXYmBxlr2uxzQx2tvBG35eQAEftUddh9VuFECQQsMxtJnCSj09qT/HIYCbIWzXLcvMxiGCD/tQcOoySlH8NIoQxZVfsftV9QWSt7xC1vcQ2csSmKWPkZVXAjP8AMu1KTR7e6RnmJWOQEcwO61FXk0cUQmGpQXMzHARV+n9ah4bu9IOXlkRRjkU+tUUtLpDpClgYtSiKlt25twvr/wBKZhueHm1QKk8t7M3WaYYH/SqfbySxkgsRGSRzqdj9qJS2MFwyMVmf6lPQfrVLAsL1ZapHEk8lvcfi2xwXX6uWjYp5NUtbh7WOKUs65V85cH0qmW1+ySmaNOVin4m2A49P+tHW97aGRzZQyB4x5gpAwfYYq9CJK9DhZ4rXyiNuVi42i/0j1qFht4bEm3v7dRFMOfIH1VORXZ1S1ZrvljOd3Vts+pFa1HVrnwcxaZBdWmOWQ8vnU/zD+1UURUVppt7BJZx2YtUcc4uVGSPY+lRlvPrfB83zNlfS2rK/lCNnmHqRU3e26Wlv8zG7C2I80kW5k9sdqjtYhttXgWWO75yq+VsY5l9MetVKtNYytf0dc+H/APiPljZNP4oCnfkWVB5Sf9Rrvek6rp+vwC4025ilDbhA2+K8DNbzW3N+GHj7qOlWjgj4iatwTdLLYTNNbBstAzecfauRy/xtdq2Ps1V8uUFmHtsEFQwOMgEgjBH3rBVR4C+JGk8eWIkiuAt0FGVYYaX+1WzJbsff1H3ry3IonTJqR1arVYhQ3rM02r+1K653rD9jxVZWCsLYpuEMrR6UjnpXMKFkNFc1gXPet8wpKnFREN0nOM4rZamyaJLCzGOaQxzWc29az1oSjMe9brXNWZqJEMO1YdwTWgcVmdiMUSRBNapRIpGR61aiTTRGRTb70vm36UljimwrA0aYUJPGc82KLfemJDldzT644DrI6aHPMQKj5oPqJFTEhGKGdQwII61sreAvyQrQKc+UUgWqr0WpcQLWCBT9q1RmKaItbfBGw/aiEtxjJFGLCvpTqxAjFVOZEhmO1BxtToth4bDFHQRjkGd6eEK8jYGayWTQxI40CPlLX/7dRs3mLelFh82dr6+HQjfTvXq4I5DY0sSk4p6OMDpSI13G9PxYo5FIdgjJPNjapCz8poW3by4xR0KYGe1c65abKvRIW7ZOOlSto2DjNQlu5VulSds+DmuVdE2Q8kzbyZ36Yo6A71FWsvWj4ZgGz0rnWpmlEmjcudqKhbA61HpMrDY9aeimFZHEgcklPI2XGTUfzn3paSPnOavqQOduV6Uj0GJmOcmnEkz0NX1RAxDvSwwA60Gsh9a2Hx71SRAoPmtcxNDiYCsEm+xoQcH+f1pSyUMJD61tX60GMvEFc9bWShxJnNbVqOvyRhPi4z5SftvW1LP+GBkH6f5jTCtzNy5YE9lqs8d8fWXBOmTMZua6bytybn/0p6munxOHK+Sz0Z7rVWvITxr8QNL4JsJp7ieNrhRh8dI/9Kjua84azxFr/wAU76aV2kttJTPOzHHiD1Y/7Vq/eXiW9TV+Jo5IonkxbWgbIUf6x6+/9KKur3T7PT/kZHeys+fnSOPZpT6E16zjceNMcSORZY5sP0/5bS9PGn6Whsyqczzrt4vvnuKjNT1aFYbd2vnFtZgiISMQ0rf7f1qM4vuIpLOC40y9kKynw/DQZI9gOwquXbX8rmO7blES4jGM7VpX+hTwXHPfXurO9tNIkmSzydjnG39K2LWGGNXMqyujebxOhrLeJ0t3lcsBHvyKcFvagLyC4a4VY2jKscYzkCoQlZ9eitHZ4EjZ51wcjofWlRXqXFuxnuVTflEQO4aoaS1ktTHzLGy92zkCmRYiSZiJGUK2Rk+Zj60WoDrpLSulvGVso1E5OZZT1Yfah7osjM4RTGPp9cUi1S4eV05cnpnPf0qycJ6Heaj4k1zahin+UpXAJoNCUGVc6dDOPFijdVPquwrZvJbYryw4CgAOu+3oa6ueHb03hnsbaFLMjlnhK7g+1SGnfDWyt50n5gkDjMkL+ahcw1Wcghtbu757ZbFmDg8gjGye4o2y4XvZQoMchlzkBwQWPp7V22z0GSxWeCytYYRnlinYZwvpipi302KLkDPESE80nL5ub1oe4fxnBI+F9bEzQz2s0IkPhuAPo9xRFzwteaLLHaS2U6FxypOn5h7136O3jQnIBYjBZxkmm5LKN4hE2HH5WYZ5KJSKaw84vHc6LNJDeQyrErZMmM59qMhkPzDzifwmiOJWz1X0A713e44d03UIGWW1jmjA6EYJb1/6VXZ/hPpVwr8pdHY83/pNEmLl4OZ2caRT3DmYhJm5kV90x2BH70nSrZLjiOPS5okNrqDiIwxDzhz0KelXOX4P29ndm71LU3OmkYmiU7r6Y3+9H6rLw9oOnRWeiwYuQwlXU5F3UDoVPrVTi5R8ewY+yB47+BPEfBcL6hpwbWNKI5zJECZYcDJ5x2rl7wR3wMsDBZCNyowpr1Bwb8dGl1Cy0jX7URi4XwBfIfJJtgc49aX8SfgTpnFck1/oBh0biBV5jbqOW3vPTAz5c/rXLjy/in8dy/8As0/Dq7RPNfDvEl/w3qcd3ZObe4Rg0kTHySD/AGr1h8MfiTYcdaUFEqpeA5ZW2OfQ/wB68qatoN5ZX8unalay2eoW+Q8boebPqB3X3pXC3El9wprUd9bM6yRnM0Odpl9RTeVxYcmvx7JVN1yPbgJ3U7MuzD0pav2qucHcW23GGi299DLzuUGWxjnHf7YqbDHqMkdj2NeJ5FEqrOrO1XJSWoKZxSS9Ds/vWeJS9DHuak8xpovWc+3Sh0g7ze9bMg9aY5qzm96sg8z4pHPTbN70nno0iDnNvWdjvTXNWuc4qmiDgPX2pQbHvTIkG/vWFqpNkHeeteJTRakGTZjTYosdL0kMBTPPWvEPrTFEEeDZrRYetMmTNNvIQM02GgYOs/vQ7t1NaaSmi+2e1PigTT7nrTWMgilM2TSObrTF/so1g1gGaVg1iLTVJIExVpaD2pSpW0UdKCUi0h2A+Si4ceGxoSMb0QNo23rLYw0jhkX/AMLan/6dMydNqdhINpa//bpuQ4G1e3jE4ZrpvWlbzAU34mQcCtBsNmqa0iJS383SpO33UA9KhLaTB+qpS2c4G9c+9M11MPQbE0XA/LjNCxkcvWn0IrmWm2th8Mu5xUhFIe5qJhYjejIZPWsE1poTJWNgCO1ELL71GxyZUZNPpMMGs7gXpICX/VS1lx+agBKKUJR60PUsOEwGfNTgmB70AGX1pQYD81X1ISQmA/NW1mz3qNWXIxnFKEoAIzQuJESHjju1a8YdzQAkyDvShID3pfUuK0PFwDSlmHrUcsg9aWj570P2USIk6704J/5D+HQCS460+k0MKSXEpxDCCWHtTqKnOSihdksi2DcS8SW/CmlS3dw4jl5d2J+hPX3NeVNW43vOLeIZpmnEdtEGNsJP+ER+Ye5qxfGTjqfibVJtKtpB8rGcynOw/wCla4V+CWta1wvdcTxiOwiEX/c4pWwbgjq2/RffevY8WEePHo/s4tjla9+in2+t3lrdTvdSvdSTKfqOQR6ipL5yWfT4VdUdbbzDxh52qLs7eOxnYzW6zOgMbcpyqt6g/wC1avEnfw7Y87XXUKPT0Nb88CF48BQ1GE2RaJVAd+Xy/Vn2FAxau8gkhwvOo2Eo60mKOWSGQT2oiCdGGx56Zn0+C2gE0l2ssrbnAyRUTwjWmfMSXEYdsDn3bAxQLPHBGEgR1Zm8xZsgUpzNK4SI+IwXmPJ0I+1TvD/Bl1q0YldV+XB7neo2XFEFaWc8+yS5Xupq+6NwAstrm7dmdhhezD9asmm8LaZZhZxEHf6cenvVjiH4RVVx6nuaDRkIkZw/wVZ6SjtcQwSFhjK9R+lWSHTre2eKRCVjKhUQDFCQkLhccuerd6k7QM5CuM4zyH0qtGdQqxggh5iIgZXOSTTwQA9Av2pVuhRTnFLCgncUGliRgY5Tj1HY0sKAc8o/at8ufpWt4cdRU0LENSZ5jTZbJzS5Rg9c0xK3KcYq9BcdHAxRfLt7UXHNGW5/bDfao9ZD3GKUrgoW7g0akKlAJ1C1ivIH8U5AX8JW35vvXM+PtClsdGtbtJ7djDJzS20fp7D0rpbMgVk2YYxk9RUJxHbLMgT5RSssXKZQN8/ai7C3E5JNBZC2hngkme3uwVZJDtFIOjCu3/Bri2biTheTTtQuDcanYviOXOG8PtzfauNfw21ghmmv7W8jktZChjA8sqeq+tP8NcTHgziq31XSwzWkmImUdGQ9mrFzuOr4b9o0ceXRnoDjHg7T+OLeKS4KWesWuGtb84DEfyOO4/WvOvxJ4VOgx2y39m1rxDeTHxo0+lYuzp6A+lemrO4ju5LSVCRDIVuMt0Kd8+w9a5ZFwwnxkPFHEM9xILyK6a10OYthQqA+XHcb1yPx3InWpfI/CY/kUenEo3wS4zuuFtUj0mZwbS+P4ZbcIe6+2a9Lxzxzp8xbShom6kHJhPoa8p6PdWXC+tQDUohHLJdKt0rb/Lsp+r2B3ro+m8a3mi8bXNkLKa202X8SOdQTHcDsTttWvl8BcmHyR9iuPe6n1fo7MWx1NYX96Bivra7RZbe4iYMM8nNuv96W0pVirgo3ofSvL38adUsaOtXZGz0E+JW+cHoaCMwbodqwXFZun2M6hgelByfSgVnb1pXisOpo1EgUz4pBkoYzUky4o0iBfPWc4oNZ8dRShPRdSBIPvWy3vQ3j+9YZgO1UoAhGTSG2Vt6Y8TbrSGmyDvToVsjkPjNJyO5xQ5kznGawSb5zWiFWoBzH+akM2RimmmFJMtNVTAcxbfemnyQR2rDIMdabZzvvTI1MHuje+T7VmDSOc5PvSg3WrcCdtHAcdq2h60nINbQ9aVLEX7HlrF23pAOBWg29KlLRiiEIetOMcwtvQ6MvrTnN+C9Imw0jhsB/7ra7/wDDpuWQYxWoWPytt/8AapmRuuRXvjz5oSYzit83MwprIwSN6VGdxmgekQbbvg9KkbeQAjriomNvNRkchB69Ky2x0dXImoZRy9c0XDMCnWoWCbCmi4JPKSK51tBthMmEuDyFf609DO3rUWkpwaIhmBJArI+OO+Ql0uBg04LoY61FrMADWJMD2pX8fS1P9ksLr/VTi3Ax1qKjlJFOI5IqlxWF8iJPx8jqRW0mJ/Maj1LdyTT8WMZyc+nvVrisr5kGJP6mt+OPWhui8z+UVrzL1FDLiMiuQULkAmtrdDFCZNIL4pEuKxiuRILdrnrTsU4Od6i1Yb0RBuM0iXHaL7IlY5cnCbk9B6mql8WuKv4Hw5La2c6G4lYjmB2A7j3qzQyBG52OAvQ+9cW4ttLvjriQafasWeafw4Yx0B3yT7bV1fxlSri7pmLkS3+kQX4OfDr/ALZ6vPqWqqw0ayfnk8QYad/5M+ldl+Jd1p1zw28F3PJY2rxlbeSI8qQEfSn/AKTvUlpenWfDunWmj6cpS2s1wx/NK/cmud/HS+U6OLPOY/EXmX8kmO3t3oqb/wCVyPHoW4qurfs4vE8fzEkxVjDAheZFGVZx3z6U4ss2k20ry4n1C9PMrZz4K+9NxQ3d7O62xHnAflI227H1FKdoWSR4ledoVCsSc5bfr+1enOf96BahdPEUBbMgPNntQb2VzqEgljhIMvlARScn2FHR6f8Axgw3EY51B5WRN967lwPwtY6BbR3UqtPdQDyFl2X2I/3pUnhaRzHRfh5d2vhTSrIV5cuijBDe9XnTrKG0txEUCE/lFdOglGomWbUo4WmdPLGmAE9wf9qqepXVhBdGWKEyzDrzrhVoe4yMSLS25Fz9CH+lb+aERMefEfsE70wzyOxRpAqsc79qWkkbSfhpkjo2arsOUQjnkkywQof9VSNiZETl5skdDUbDttI7fpRkE425ckg4oexeE7CXZV5xnb8pomLlB5Sce9R1vdqPLnBotWByWPMD3FBoDQ+8gjk5A36008/nI5ugzW8Y6ikELucddqmhDMsxdPKBmg/GkzljvRDjqo60I4cOQV6URGOiZvzEU4LmP1xQhRnB2O1IePnchdqOOANkmsgKkZG/ekXNuLmPPOy+GebY/UPT/rQ9sGRWB7UWsmDzIMlf6U1YJkc84hMt1bPNJd+HyOVhVtvCAx1/eq5c6MsNnmB1MdyochfysPSukazoOn6ldIWjQxAkmM7eJnH9qo3EdlcW2rC2jheKyC8yv0VR7mp7F+S36DxzLF8ItdkuCfndOjOmRueuH8o/vV04K05dB4K0KyjHIUtvm5RjcSnc1wNZrs2Etmr4tdRvomde2xzXoY3A5YgnRY1AHtjpXn/yNfxrqvs6/En3j5Ob/G3h62g17TuIRbwwm+jMd2zj8MNj6yO/eoDgrVrjVtRj0+XiC3vorNwIbdQUMy9sZNXL42P85wPYWEKLcXFzqaRwcw+o/wAn2rifFtpdLqsuqW8FzFFbuIJZVXkW3mHVciun+Ol/2lvs53Lj/dnfda4d/hJivJrpILOccySI2GjP+odqluFOJLXUJ24fmu3uNUiXnjLdZk9RXGU1++4r4YXUobyS4vtO8l/Z5z48X/mqKTwDeXV5xzo7wPi6g5nkkBOZIj0BqvyFEbKm2N4c2pJHoRX5wD0z2FLU96j2u1M0xQeTnIWtJdEg7141VN+DvdiUDY71hI9aj0uFOck0r5oEbHar6NCtC2kx3pDy+5/ehGnHrTTXIPSijB/ZNDA7fzf1rYY7+Y0D45/9mlLcAf8A/aYqynIP8UetZ4uc+Y0F46+9Z44GdqONbK7BZlGOtNic5H96GM4PSkrKAT3p9cGKcgzxfTP70nxTmhvmF96zxxnoa111MVKaChLmtGShhMPesMorTGjRMrEEGQVniAZ96Y5h6iteKpz12pnwAfIPc2/Q0pXyKH8Ye9KSZQO9InUxsZIIR6XnG9CrKCc0ozqKw3VsfBoJ5iR1pIfrvQ5nBG21IE49aySWD0G+JnGKd8X8J6j1lA707JIDC/mxSmgzicErC1g3/JTckhIY1u3VmtrYYxmOkOh5TXv0ebbEq4396cB3ocDApYbBqNFaGRNkURE2+560BFKAQM0ShI+4pUojIMkoCD1ouFwFIBqMik3oiJzg5OKyzho+EyRSQY60/BIoJ3xUdG+M96Jt9xk1ndWjfkJRWBzinY0Y5wKbtYyV370dAgQYoo0sp2iYYXPXaiUjx1FORJgbinljz2pipAdoysJxRek6Xc6xqENhageLIdyfyr3P/KtLEcmrh8MLPxtbubsoCIYgnN6Z6/7UcaV9oXK7wF3HwkjSDms9Tc3HcyDKt+mdqpd9Y3WmXslnepySofuD7j2rvJ3HWqpx5w+NV043UC4u7Yl0YDqB1B9qJ1xYqu1/ZykxkdN6b5D6U+pLgMm+2T7H0rRUmkToT9I1Rt0YVcZ2oiJMLSQlEQrmufdQOjb+yO4q1FdJ4ZvJubDuuAfQVDfCrQflrSXX7hfxJh4du35lznLf1pHHh+eNhpIJPzVwI2HtV8t7SLT4ksIgFitlEarjofXNI5r6VKEQK/M+xrwwGOFYt6hsfeuSf4gXbksxBAzWhIPOD1b0xXYAmOma41/iGkv7O4065VY20yYcqoTuXGd/6/0pH4b/AJ8Hcp/0OWRREQOfmmUE+GOTYqPvS1mEqsOdVtJUAYQ/UW3/AL1uCGMWxMjeHGymSV/THtVpthoUemwS29k9pLJgSrJ9R/1qPSvYnKTEcA2Y0fUmMk0T28i8zOy4CD7V1C0umhiDeNy3GNoz0dPU1TbPTbSLT1ttOjW9LMGmlY5Lj2qZ1Flt5ITFLHM5TLEjHk7is8x0FpM6tqAvoBHbqbZY/qcNvI3sfSq/d3tra25WGd2hI6SHzUie9WazM7NGm/IiKfy1BXcvjPlsE460GBrwGHUjKSzHI9aJt7lmBPMBtnaoFObpnb0qQtWbm8uwxjFTBqZOQzNsxORR1tKfqBA3qJtPMACdqlra3DBUB3zmgC0k4SxUgqM9jUjbyNGoQq2PUDamLaMFUBG9HCKWEZxuT9PaoDg9iMLjnDk+nSsKcqZIpshkU8qAOFyw7Vil2RRk4znJquxFEbeNVfn7DrTJBZmIGdsk0WIJJFORhe+aU1nJy88SYLDBU9MetWpFNMCVFbOR1ra2qEkmlyLHCrMZlwMYHc/pSJLuG3bEjYGM5o4yAcRwaeTnlYL96SLdogMqSCcHFQ0/EkMEgktnLBjjz7rUjY8QrcStbyAq+MqR0ejjguSbQu4tSJOQwAKvSVTVO4jsLj5a5SSQy+I2ERB9S+ntXQJEjcM0b45RkKTt+1R2oWPzUEsSsUJGQ46j2p0UkL8/ZxbVIxZyt4Sn/upWQRlu4z/auzaXq/8AE9Ks79QA0kY6eoHSuX8Q2fNdz28lu6BcBnHUjfBz+/7VYvh9qCXOjPpjNyahZtzmLqfC/nHtXP8AyVPePbDTxLHF5pI/Eh2fh3T5kPJNp+oLLEfRx61B/EOxutc0i71jSLn5O21FlbU7NV5lMq9ZF/tVqv4V1fS9Q0/Chrm3PhHH/Ex1qs/DrVZJLP5KUDwnU2kSnzK0g+on+lZqG419v0NtSk3/ALOWcPjWrHiCwXRFeW/k5Yo4k/4690x3zXY+FrPT5uL7XibRrV4dPija2vRJsYrr8ykdgNqHk4f0Xhq9t+KLHx472wvhLGit5Ac9V9vajbrUotP+J16qL8tpXFMS3cXLsizkebA9TvWq1/JV4Ecetxt8lljuJAgVjk75boDW0uWXoaj45ZApMgCsDuq9qUHPUdK4Cpcnh15SS+yTS7Iz1P2FOeOBjlbyn9/2qC1HV9O0Kxa/1a7NtAv0qN2l+w9elREXEPGfEQ8ThzQ7bTLBvou9R2JH/v2rTVw2vYh2/ouhdzuUlX3KUyJuYeU/cdxVR/hPH8blxxLpksv/AJTH8OmTxTrujn/+7NEfwM/h3lguU+7e1MlxFLxpSvxeS5i4Oev9a2Jc55jUTaXtrqlol5YXUdzC4yGjOaeMrYORt96S+O4kVvYkfmsdzWfOD+aotrkVnzA/WmRqI5kl8yOzGk/Mj+Y1HmbC5BpAnJp8KBcpkot3zH6qz5j/AFVGI7DenEJz1rVXSxEpkkJzvvWePnuajxIacjkJzWuuszSmFiYZ2z+9OLKRnfrQitk06fvRuGAqY8k25yaUXOdmob1rcbE5zWeyrR8ZhSykDBrRlJ70wzUkvisFlBorsH/FOOv60g3BFDSSY+1MGYnvWCyho1xsJBLk4rbXLeC9RPzIDY5jWPcjwm8x/es/wDFMoUH/AMNa/wD26xk3NLtV/Atf/t06q5Jr18ZHAaAjDnNaaE+lSCRgBs0hotqLsCwFYzzZwKJQ9dqzwlHrW1GKsJDsX3p5H60wgK5p1O9A46EngTG3MKlLVMoTnptUdbgYbapw2otbWyu0fnhuF5SfR/SqVYPcLtjjFGRYPWgIWYMUJ5gOjdM0ZDkE53pigV8gcrZ/SiICWFCwtj3oqJ/ai6IHR5RXQPhZCPkL6cD/ADJQPvXPAc4ChjIxCqAMljXZeENJ/g2iQW7qFlI5n9zQyWFOWkzy+9IliDoynowIP2PWnaxqDCl4OIazYLp+qXlo42jkLJ9vSgWXcmrPx9EsPEjsPzxDNVrl6+1X1GwYhevSnUwo5ScGkDZjtTo5AzNJ/lqCWPpWKcfI7fBWlt5rzj7TY5eUxRQmQg9m9auWTI7sdyxyT6mqNZXnjce2EsHJOt1GVyZAoz65P/KugPZTWayG6e2hjjODK1wmD/WuZz+PKcv6psbRNZjEcreprjX+JJ5ZdT4fLAJAmVRF6Z9a6nHxfwibr5ZeL9LNwP8AhEn/AJ9K5v8A4mBfQnQwYoBYuCIpQwZAfcjp+9I/F0Tq5H9kMvmnDDkFskElnPJe+I6BuQqm3M3pUrdrcalZxglJFUBYpg2GQfye9Qts4EKIZSIlbxGEg3LeualdFvLaF2iu4naEkup7ff716mTzyjnxJ7gfUrrTRdzZVByiLlPSI1aJLqG5tXXkQOz5wBvjuft7VRJ3SaXNk0gs5tyhOHZ/epq01LlhHLKGULyHOzCkSH1hcqpKwbk5Iojgr3b3oGSJFOBvTonkkflff/VjFY8Bc5HehTCGobd85xmpKBOU07Y2auuGaQ/bepBbUQRsWUVbwKLNwRAHl9s1K2KZ/Q4qKhnzKfIelTembYaUFctkqf70qTwdHSesoyQrBe2KkBbtGjF3DITkEUFYy8iAuw9vcU7eakj27hGRFXsDQOxItVtipGHLyvkIy5JAyajZ9TCSZ/pTNxqjYyso2GMHaom+1lSuGhZioxlRsaV8iGRgSM/EE0DvIsQeBRg71Cah8Q+VipVlcbLvjaq5qOrSS/hLOqRYyQKrV3FC8skk07sx+kUyvyDJEvqHHV5Iss0NyBnGQwqIg13WdVkQWkk8ksg6t9I/SgbHTo7uSTLhxy7+lW6w1LRNDi8KScliv/BXm/tTJzaXgXGCftglnpOsSSp82zx8/Qjdf2qS/h2qWrhfmDzIc839vSj/APtQpA5dE1F0I8j8v1f2pg8c6SrrBe29zpjnoZYzg/r2pMbJDYwj+wux4nvrORJbhi8OSu4q7aVfQa1bG4t3Bx1XuKqVvZWmoWgMF1DNz5wE83P7e1HcPQ3Gh3PiRjlhb/N5jsKfXd5wzX156I3j7SovDN+pbxF2lXO2O3+9U/h99Os+LLC1vNWl0SSRg73SJzBl/lO/0+1dk1e0gvbVixVo5Bvt5TXnzj+SXTOJYyVOIwFVTsDWxZP2YW2np2+11Ph2C7uzcatLaeEOeyATa9wOg3qkcLaXepqGpPFCLbTfHNxG0z4/EbquOw6U3q0kOscI2moAD5q0ImUxjIA9M9qsnhJqVkZVcIksSTOufqJ9KbHhRxr9gu97oNxqXm0S/wBLtJkkvJAGiCdEOfWmtX4W1zVOD7a1S2abXdPgW8ia335eU+bFDrCgKlRggAZHf71YIQNV0RtIN/f6dkgi4sGxJyfmQH3yKqXFhGOIJciUp7gnTb+413Q7PX47dxDcgGZ1GVjkHVWPat3Wp2+mWFxqFw2IYELMAfrPoKrHD9/q3BN9q/C9reTNp5j+fs7CYZjnB6qf9VH6slvxPfadFCj/AMNjUTMo2846qa5suMovTXG7sa4f0WXXbscUcSxie7l81lYt/l2sfZmHc9Nqtsty0xVpSxPoDhcew7VH+O88jKE5yo5l5NiE7ff7ViySSjCKWx1ycco9TQShKXkbCUUEM8YzsmfTlpIumhJBbmRh5433Rv09KHCTO2DGB9mB/wCVMm4UHlZxG+M8rqf+dKhTj1lysTIy54ce2u31PhZhaXY801kdobkf6R2o3T9aj1m1a5iDRTp+HPA/WM+p9qcM7Z5gMODnmB2JqI1dZbdjrtnvdw7XMCDe5i77evSmdd9gppE0ZcmteJ6nf71HxX8V5DHd2hL284zEx7nuP+VbM7HriqVRPkD2nC960sx9ajxOO9OJOpzvWiusXKZKxSZG5ogNUVFcDfejElyMg5rRCAmUtC1NLiOMjpQ6yjFOpIDuKfCIhsKQ0vmocPnpTudutXKJSHOalAAE700TitF9vWkuI5McZqbY+9JL5ptn61nnEbCWGSNmhpZCuQDSmehZWOXrJZUaITNM4BrQlHhsMZoZ5vXb2pPieVu1YpUmhTIO0U/L2u3/AAqJRNulOQR8tva7Z/Dp5EHpXZ7HLGVQY3Wksg9KLEfMtNmKiTKaAmjA7U2IwRRjrsaaK4NNTB0a67Ypa5FbVcmt461aK0Itsk7VKQzOIhDzHww3MF7A+tR1qOU0bCwzRxAD4SeU79KkLckrk9aj4fpajrYnFGQMhIBwT06ntn70XGuGAz1OKEg25jt9j0J+1F2kMt9d29laxPLNM2BgdPc+lT0QldA0+z1GRp59S+WazkBMce8hbfbH6da7PZypcQJJG3MCAKq2ncPaXw0ZTbWUct5Io8SaQZ5+v7dakNCup1vZImjJik8wIP0+1JZSLEN60xrFOaHu7pLWJ5ZDhUGaFII5dx5cfMcRN3CxgfeoBVzn3o27uG1G/muHO8rYHsKZVM1HLEFFDPId6dNvzwXiPtmA8p7Zp5YdqXOFisbxnY+HHHzPgZzt0HvWKU9kP9I5JoejafxRHZ6Vq0VyLRrgqJY3KMH9iO3TarXF8GOD47iRdQOr6wIjjwpbllUn12qs6/xZpUPyOipY3caXiM1i8R5XikzgFv6V1jQJ7u+4esptSCi5iQ28rAbkj81Y/wAhKcEpJjaEpeyKHw74DuIflJ+DYfBHTw5CGH/5da5J8YeDtV4I0SGPTdQn1Dg+4YtDBP5msJP5cnJ/Wu/Kgc5Zfv7VXvivDp0nww159SlWKCPlEbDp4pJGF965n43l2/Mo+0HfVFLweTbadbiYiZeaNUzjO5/SpeK9+agigMMYVAfDx1xVbtS0JUuCJPzEjBVe2RUgiEoHHlYkAH0Feu8JYjDF4SwHgmCzjmJKN5u/IaMieSS5IKhV/wCGO+aj4OQl8jlmB3xvzH1Bo+055fNI2zHZsbr96RM0Vk1bSSTxOjK45T1x1qa0yyuLyRLZIW2HmY7UzwtY/PzR2/Rpm646V11NGsuHNK5rjk5mHnLHcUuPkJlYk0qHT4FjTaUDLHHaq7dyHxX5vMOxzijeIuKLfLckvlOxb2qkX3EsPhSMJsMDijwieFkt9RjiOfKM9M0XDxXDbKsRPOGbJJrl17xM3hDkk5X2+w6/2qMbXLmRmjkuPFU/mxihlXoSuw61LxiRKE8YDHQ57UpuIllYsSST1wdv2rkq3x5RzuXb+bNER6tJGcq5+2azyoNFd6Okz6wJc5cA/lyelC3F3PLzfiFc+nSqxpmoSXMqglWz0yM4q+2vDn8QtDLzAHHaldMG99RRr25EfOGfGfaoiWZr9ndsrH3wasut6GsLNGrFmPqKhUs5Le4ESRtltt1706HgVNkbdyXc0wiSX5O0iG74xg+lO8P6zHFdyxafepokJX8W5kXxZZPsG/WjLvRZdV8WW4d7WwtgBcXLD65P5QO/3pzQ+Cbm+8Nbi3WGyV9pGXzt7inqaijLKDl6JDh601zia8ms9I40AktF52a6HhxBfvUfd69xa8txp7JFrVvDJh5ki5lf7NXR4uGOF9LsjbXDxxKu7EvyiUehNP2/GGmxYteHrS3SMfVFHH5Q3rmh+VfoKNMs9nO9Avb3Tb57qwgk00/8WylGUX3Wr4usx6nEqy+MWHRVGA/3qUjs2eUS3SWjSudxIMnFSXyUUUXOkMCDsFGaqKW6G4NLyNaTqE3gCC5tvAibZEj3xXPvi/w62o6Z/EoYczWTfiAHcp61f+R4ZXmtQHVvyN1FM38QuE8Pl5g/llRhny1qrZlsenPvhlqMd3wtf6fcQSyI8Zi/DXmK9d/6VOcMStd8MJIu4s52tAx+rHbNQ3w6gu+F/iBfaFbYeOVDPErMArKM9z+v7VP8G211Br/FegXCRQ+PF83CgcN5v9q1RmZeoVPamKHxgp5OgIHU+lbiYW6I5cpy+n5fX/ainYvo9uXc8qErJy7Yel6cIruWW3mHknjJyezVfcihhBcZW8k1lDqtu3Nc6cTMzgbyJ6CiOGXGp6do7xPDC04ZlZ25Uf7mmH1JE1CxsLtgkc8rW0i9gc45v+n9agda0ebg0S6Y1000VteKxjzgRhzgcp9O9KlWpMJNr0dBvLDTrPSWkuOKmS5sn8aWKFchh6ZoTiK0seIrKz4ktriYWrJ4PgoxQlvV6Ft7fku4HlEMeWDEZyHPvU8s3iW17YhFRHHNyINg3saNwj0wFyZT4+HbO2bxLe6vLORepDkgfpRcFzr9vGyG9t9Wiznw7lAn9RRUabH+Y9jSjaqc5O/2rnya3DZCP9SLl13T45OS+0+90uY9XiBeL99qMtP+9/jaNdW1+APphbmlHr5f2olo38ExGTxY/wCRhtURLw3b+K08ET6deAbTWTcv7+tX2iTqyv3N9Hwvq/kJ/hN+xRrdtntZOxx2ztU9MSrFd8rufTFTmv6rBxTw5No+u8P29xekL8rqdkvIQw7yjG/71AQ2clvawwPIZXij8NmxnJ9anaIPn9Gw4381Ljm60x4TjOx/alxwsM7UyEkU0/0GQzjJycUZFPyjrtUYqNucU/GrnYHamqaFNMk47lehzT0cwB9KjER896LhD8u+9NjYgepKwtzbeven1bPehLZcoNjmiFjI9andFYxfiD0pLNgVnI1Nkvih7IJaY0lMNLgkVt1Y0wysTmkzlEakzby4pln3asdXOdqYkOO+9Z5tDVoxK3m6008mFO9JlJ3oWRyFYelJ6pjFJk5FYkWlicZ/Bz0pK27D8tWGG1B06yZiN4QOlDyWagYovkQvoQzRFcbUyy4GalJbYYPLmg5oSEamwloqSI6Ub5prlzRMkZO1NcmB3pyKwaVQK2FpQG1Zn2pgA/AB1zRsajJxtQMTD7UVG/l3NFFg4GpJhTR8L4HSouN9lblzvjHc/b3qQ0jT9Q12/wD4fpMPzF2w6A4EA9WPb7UeookLVZrm5htYIDNczfTCu7Y9T6Cut8H8JNwvaSS3Lo+qXW8sgGyD+Uf3pfBHA9nwpbNJHJHd6pJ/nXLnJ+w9BVnMQc+ZfelykWR8qMUk5iG6ke1P6Na8kbzFcM3SsntzyYB3Ow261JxRLHGEHQVWgmRk+lVjjvUPltL8NG80vcVathXNePdQWfUo7XP+SmGBG2aFPA4rStovkXbcU6q4bFJTDkcu/tRcUJcZG5rNbYPrgNqo3ofVOKLHg2WxeaNLm6fIEA8w5SOre9StvArNMD+SIuPvXnnVOPdHS81HxYbi81EuYgWfZCDj02oOMk5awrViHdT0u/4g1OLU28Bvk7staMBgspOcN9sCuxfDW6mv+E55Zmy41BkVsbL9zXHeHPiTb6TpMdvLZwyyzk83Pvg/erp/h316fXuIeK7F5AmnRQLLHB2Vid2zQ/kqO9YPGnjOn6hd2HD+l3Oravcx2Gm2+80zNuR2jX1aqbo2k3vxT1yw4l4ispLHhPT3YaVo8y4e6YjHiyr6Z3pGk2kfxW4vu9b1NvmeFeH5vldLsjtHdzAbyuO+K6QWldzJLjnC8q4Gy7dh2HtXAt5MeLkK/L+zY4SsZ43+LOgvw18QdbtAuInk8SEAYDJ2xVes79ShjkTJOOXeu2f4qdHRLjQdbhjA8WPwJG6b+9cJgRYboFhzctek4dny1KRhsh1lhNWcroixyY5y2GGN1+1TqWctvgHlDsMgE9fvUHZS/MzKitspx03PvmrZa6LLblZJpJJMjp9XKKbNDIlu4TkXSbFrsopmkcoh9DULxpxje3/ke4cxoOU+9O3cj2ejRyboyOSq53Arnmp30s9yI43VlJ8vff3pcfAT8m576SfyFy4bcgHNDyaTdTRqgLYkffK9P61J2SW9nCZZECsVwSaBvuNliQR2CBsd2FXFykVLENXHD8sgknl5IebGQzeXv2/WomZYoQQLqLboF70xcaheXwZ7iZmGQPbfPb9K6GfhRxZw/oNvxIuk2eoaY8YlLuuSq+4zR/4+GAouRz6JJ5f8hGkA9N62ryxvyuCDjcEVav4vp0A+ZXSpNLYnDKDzxufbYUbeWtpq+irdBhE7HYMnKWHtQyaYxRZG8NHluIwT+ldx4acS2vIvcelcO0W3MOoKvMTvjpiu28KuUgXBXmxkgHOKzv2aoegDirSnTNyi8qK3pnNDMLd9HE72qHkHmIXz1e7m1jvIWQpkBM7mqdeaU9vNJJaysnMd1xsKHqwkimS3E96vJpmmMApGPmRhT/8Aj3oGfTeKr1fEn1aKNW6LAP8AL/tV/to7jk5WiEzKPKcfTRMcbW687WUQwMv5c89X3bK6Yc6s+FdPnlH8V1m6v5hv4bEiPHrnerHDo/ysSLbsLVc/8Hcn9al47C/vWeY2EETg4EcSbcv3oqDRrlmIaDHMcjA2H6USXYr0C6Tp9sr5eCSYD879akL9XI5IHdfTzZxRI0i5Cg+NgM2NhilXOkXJVo43HM3enV1r9guZAw6k8dyUYurjqx2qXWdLiJ0ZgGIAL43NM3Wg3WCs2GI6MooQymzIjnXuAW9KbFYZp+WU/wCINsNL1fSOIIkLJbTJDNg8vMnrn96O1kwcMce6VxFp0CppuoJiUq5bY0rj61bU+G7uGJscg8Q59u1Ux7234g4Rnu5buRbjT1jS3tk2Gx3JOft2pqEPF4OjXOowxJfWUbfhxz+JGPXNRb6q0UyuhwUzVXHELX9utwWHiPGA+B196EbWmPfP60QL8k1xVdk273kZBKyq4z12Oc/rVr48sTxFp0d9EixDW9OS5iaXbJjGNvfvXO21IXVpL0dl6ofSq5c6hqV/fw2F1qF3Jb258KEBjyxZ6Ae1RyASLBZcZS3GlIssjeIqcpJ33FXLgrjbU78W19dIk2nxsIZxH9ayHoSP3rj88VxpbXFlKOWSNim/ce1Wrg631KO3GtWQSO10mdPmBuFn/wBTeuN/WhjJalpbg35O1+DbzzPNbspQtgN1GfT2pwWyp0Tl+1HyWluDFcWcQigvIRcKmcqSe3tS0jL5IH01yb7es3p0aY7HSL+TVvyCtjT0/MhI9M1MLbe1OC3GM42rHLkYOVZXm04n6i2P9O1NtpaFfKvL647mrIbUH8ta+TGCMVFyv2X8ZVpdNHYU1/DwO1WprMelMGzHpVrl4X8ZXV0/0FPR6eOy1OCzA7U4lqF/LTI8wCVBDLp+R0ohNPx2qXS2Gfppa24/lrRHlCnQyPghKflopY89RjNEiA+mKdWADqQaJcoD4gHwPRc020JHVRUssPWktbKe1F/KX7IqCFa1OScUhrI4qbNv/prTWanpSZcjRnwkA1kcdBQ82n57VYHtcZODTZswR0pEuQEqCryaYzc2F6UNJpykN5f6VbDaDzbdabawwpPKKS+ShioJOKDGm2AAxmEUPJF1zUpAgOn2H/2c0JIOpxTfkW+DMmREkOSTjPtUdcRBebIqckjAY4FBXEIcHIxW2iaQqS0gJ48k8tClR0qXmtipIoGWEnJArVGSYtpgRQU3j12oxoiO1NFaPsL8jOCKfiPm5QRkrzDPemm2IHXPSktJLyKI4zLKJOQBepPsO9FoRO8OaVfcS6tBpOnoRcSDnd2O0KfzfevQnCXCuk8H6ebXTk8WWTee4YeeU+5/2qC+FHAL8JaTJd3jiTU77zyn/wAsfyiugABR5AB64GKIWIFtC3/CVe+1O8gA33pPiLTRuYwrMWAVBlmJwq/c0OFDrKrEbbg5ps30CSrE0sYdtgvNuT7VXNb4stLTTrq9kvYrHTbY/i3spwCd/KvqdqoXCthqnxC4kteLdRW507QbEcun2pYh7j/WR6dKvCzr897DEMu+MnlA9aouq8D3l5cT3ttqEUkshz4bnpVknieSUu2+dgPSkxoYQArZ98b0LQSOfy6deaY2L+3MRHV1GVpULc/0tt/pNdHEySqUmjSVT1DjIqNvOFLK655rRxbv/L2rLbQ5IbC3Cs2ZAuQ0nlVwUz1xXkD4l8Oajwvxxq9reW8kC3E5miLLgSxE5ypr2VdaRe6ewW4j/DP/ABE8wFVrjvgfTviRw3Jpl4oF/bjNhdk7o38pP8vtWKm50TyS8DrIqyPZHjlXcx4JB5N8ivRf+GjhuTT+D9c4oMglfUg9skA7cozXHeLvh5rXBdzcaXrDRG9MYwse4K/zA/7V6K/w/a5pd78O7Sz0yMxXGlyNHdwN9ZLDHiH2NavyF/alOAqlf2xifgfeQycG3FgFVWtbuQnHVxzZJx/SuhcnX36VxnTpW+HXxVvLVbeWeC+kXL83lhiYnmfGOgxXaiyEjlYeGyh1I/MD3HrXlOZRJy7o66yGNlJ+MvC68V/DnU4ynNc2ebmIHrgD+leOI+VerZkP5cHOfSvfV0tm9peR3V6ltBPEYpOhZVI64rxLxjo9zoWr3NhJOl3BHO7x3SAeVT6n2r0v4auxVZM5XJknPwB6LMILlJJPww23n2rqum3MkFvJJbKoLJ5jLuD/AGrlFjIJbkOCjgNkHrn9O1dV4elW9t4gVTkJxysevvXSsWAxYJx5cracPaetkCPFGSfzMa57awukTSZ2B8pI/wCddL+KckaW2m5wIkGBvjf0rml1qaRxuIkwr7AdcUCjoW4Q+p6lPOzwq58POOfs1Js9BmcJJOpRHHMD3x60bZWD3NyrsrCFN2yNifYd6mX1mKMtkZWNOVmK+Uj0X1q+2eiKt+wjROF9MnSCS9km8QkDlXoMZ/vXUJ9c4at9PiTiDXtTlECCJbW2bEJHofWuSpqGoagALC2Ijb/iSnlFHWGi2UMqyahLJfzfmhVvLzUp+Xo9SRdU4g0/UomstA4btmtnbyG8GwPrnFVjiJGMsVu7r40Y3RB5V9hRs2u29igsNOiaeVz0TZYxSW01Z0MzBnBOcuN6DWMUftENYQO9yZeXDKc59vWugcPXrKxMRwTgEiqeYzDzJ05/L9hVm4btGZsFiOTGCO9UvJa8HSrOZXRiT1GKjNSiEUjADGaktMh/BAPXanrzT0uITI2+KZhE2ivWr3LTcqBBnripOS7tLHMl7KscY+ot9P70Je6dc28DMilSRgcv/Ok6bpLapC63X48cgwEb09cUuSLi/wBhdnx3w5OSIr6AHpnpk+lGpxBpF1LmGVFIXmJI/pXO+POBNO028SWBBESPJ4fTm9cVQk4lm0OeSOVZQT3elvfottM9H2r2NyvM1whUnPL0rI4o0GC0bSn6M964hp/Gy3HIfEb35TsKsdtxXPdRAFuVOobuB60PaUUGoKRerh1iP+YGcfl7VCanDFe27+Hvjc7VCJrrpzZYMcZzmm21d4ArK+PFG49K1VXOS8meynq9A7qElZbCXLJLGVPtmuXaPiyF9YpdhLxpDHySHylc9zn7V1K7u2vImeGULcR+ZT6+1cr1jwbbXpLs2hn8Vt4wdy2evtWqD0wWLyCaRPFFbTWsz5ljOEKnYikJOoZhzYwM796GnkkTVZ/EjWIuclQNhWtQljFw4QdFzt3o2BpIabdoLpGaTAJwVx1FXbh+zttb4V4h0CC2i/iluwuUkHXAGwBrmdtKvjBiMAHP6VY+FOJrjQ+L4NQWQ+DORFMceVlxuKXIuHll1+HCcOcV28dtq1ms+rWrYCSnHi/r3q+arYWycM6jZ2tlDbW7REBY1xhvce3vXMONtHXQrwzW7tapIwu7eWI4YZ/KMdT7VetA45t+NOGruw1DltuIlj8F0XZLyPu6+9Zercu8foe7FGLTLfpqmbRdLjY5MNmqg+tHwW4XI9etDcPhZdPi5WBEEQiPual4Yc71yebcnNo3cVbWmNw24I3FOi2XcdqKiiJH00/HbrvkVy3M04R4tFYbCs+VI/LmpRLYdhSvlqnZlkK1sP5aQbMfy1NPakDpTZgHpQuwtIiPlU9KUtoPSpX5c4+kUtLU/wAtSNxMItbUDqtbW2Uds1Km2JHSt/LY6LTY3g9SI+W9qUIf9NSbW2x8lYsBb8uKL5ydER4hGM5rBbue2KklgAP0ilC3JqfOToiN+Wk7gU20LDotS5t2FNvCanzg9SLMGQc018uM1LGHPakGFd9qVK4NIivlxTcluwhfbpUyLcGkyWymJh60n5BvUBiH/h2n4H/Aph02o20Qtp2n7f8Ay+aQ8J64rpRkchRIyWPY0O0QOxFSzxEdRQske/StULSdWRElv9XMtBS2yMD2qbePmUg0K1t2xWqu0roQslkoFBzQEZwOlT8ts3pQU8AYMCO1aIW74AdeIgWiOxzg52q/fBHhH+P8QTa7dxZstObkhU7hpe598bVVINHvNYv7fTdPgeW4u3CqwHlRf5ie32r0RwvoFj8PuF4bBHPhwIZJZD1dseY/8q0R0zSeFkO+f96Zdsdd19B1P2obS9WsuINPS+0+4Wa3kzh1PcHcf0pma/lllaKwQTzL9UnRE+x9aaAPXd9BYxc87kMfpjUZZj2GPWqpxNxBZaRpY1bim5+RsdzDZp/m3B7Ly9zQfFXGGl8A/hN4+vcS3h5baxiHPJIe2R+Vfeh+Fvh3fanqsfFXHsqX+tqC0Fkp5rexXsFH5m/arIRmi8Kap8Sr+31/i6FrLRLdubTNCA5Q4288w7nbpiuqLAqEqsYHl5F5dlVfQf0p9F5h5QTgAdKcRUHlG3qvWr0sZS2Ub1trRd8CidlHrSRIDkA0L8kI+SBQCAMGsAVVYYBzRzqjDJG9NkxwrsgbHWrICnx1jYQBHH5lfpUNcafYXchQeJYSv+Vvob7elWFJLacbdfQUiS1huEZZgJlPr1H29Kz21RmsaCjJx9HNeOeALPi7SZbHU4Es7oqPlL1N8N6E+lefuFbzWPhH8ShaaszWtyhEcx6x3cP5T6bfrXrefTbmGN/kZFmUf/Ly7j9Celci+PnDdvxRwZcymymtNY0c+PG3Ls69wG7isa4rjsPpjY2JvWb+MWmCwTT+NLQrNFbJ8pe8nmVrOTPM23UjNRllxtxZpvD1no/Cy2WqavGWnS5nOYhZ/lXJ/NUbw18WLvW+CNH0Th/RH1J7K3/8fEsXMqW/58epqizXbc15BpjT22lSyHw4efDqnYBu2KbxeAm/7jreTscN8R/FHiLju9WbwoNL1mzBSa1weWVR7bVXo5YeIbWV4oDAUys9vKd+b+1O6hpUsoNzBKTqNuuY5u8o9CaGvZCIk4q0+ExSRqsV9AB1Pc/p612YwUY4jmptlTaFtH1UIhKxOdgav/C9+8UjQuMkAFMnHL7+9QOv6eutaLJqkCp4kQ8Q8h/qKb4dvfmILdiMt0Y5xkCslq00QkW/jDUV1WK3gaITTKcqR9IPrUbpPBkLo95emOPJ8q9Qf0o2yK84Ysn2JzT91fLFdAw8rqu4X2+1ZmzVHMGbzh6O1i8W65IxIeWNUHQUONL8XBg09VVTkeL9K/YUG+v3GqXLSvKWYN5UA/pVi0u1u7mMSyCRnbsfpod/YcVpBNpUs1w73VwUTGfDj+j7Uu10uWR1hsx4Nu25fGXY+xq4pocl2CXVYo8Z5Mbn9aItbGC3U8qrkDC5P00NklFeBtdab8kXpPDVpYQ5MXUfqfuaZ1G+tNMn8FwXJOFA/N9hROq6vNpcEgjKu77KRviq9w9a21zq0k15cNLLHhlBOQvXp+1VDyhjyPg3eSSXMgd4/DwckY6VbNBMUKgk4Jx+tETWVjLa/wCYhLf1qq3GrLp9zyRyrheuT0qPV6KWb5Z2LRBFO2GnjQYDKWOxqXt2sJUeVpl8RDgqD5TXELDi9Cj27OY4TvlTvUhbcUkZaK4UYP0MaXK2SG/HF/Z0rUdXsIAeeXm2yNu1QWpce6JoOnPdzy+G52TlG/7VQdc1mOO28QP4zyN5MNjBqHi4ZfUbpdS1m4+YBPMqMcKo+1XCTl7EvEXXS9Vbi8Ta7qFs0VnF5bZG2Ln1ApjVdEs9YjHj2qszL1RelErIgcRouLaJedSDgR/pUmk8KDETjmK8/sV9akk0RNHKtV+HbW5eTT7hkH8jGomzutR025FtdxuXPQZ2K11jUI5ComaRFEpAHPtgmq9qljb6rHJbyuoK+RZEHmDelUm/snj6I+2uGnBAZFVhhjmlSXMRUKrFuTy7j+tRdlbSWNzNY3K+dN1bsRRksKPGWUhWO5TO5o0v0BJv7Ms9QeKRycc2eXB/N71Ute5m8eVB4XK/Mcbv1qwfNQG5VWBKq4ViOpJz/aozidmtJZZrfK5TwwQMn9q10aYLWU66dGuI5Ekdy31FjS71pGcO6gKwxkU7/BdRlsUYafMVBzkDcj1xRWn6PqGu20cGn20lzIrcsgVfo+9OnPr7FxWgOn2Ut3IyI3Kn5jjJxV4s+EDdcA6tcQqz3On3AkiXGWWPv/vS9F+EuvLIks9zDYjvhsn9q6roOjW2jab/AA2255o7iMpI7HzXA7/bt61ktv3/AARppozyyL4ZtrD4h/D6G1vQsTKRHHOvW2kH5gaheE+ExwXJqGra9JEk1sDHaMzZCpvuvr0qatZtG4AtDomlGW+uZ5TKttCOaUv/ACEdh70Z/wD04vOMdMnj4mvms7+ZA+nWyN+FAd/LIfQ5oFdCh+X7I6nPykTfws4s07i7S5LG2UW+r2js8ludjPH2Zf7VcIB5l38pO3vXlT/x7gjiEQyyPp2saXKCsr+XGOx9UPY/evTXA/G1l8QtA/i9vF8vfW/4N/ar1jlPRh/p965XP4nn5IG3j2pR6Mn4gAaIRQ3amokwAT3GQe1ERiuK/eGvwzap/WleGMU4oO21LK5quxARxtTYjzmiyvfH6UlV67UpyGJDCxjFOrHTqxjtTiJkUvSYDqu3SswfSjFiHpWmjpmgghQnbNYIQM0T4Rz0rPCPpU7l4DBP9NaEZJ6UYqZ7Vnh4qu5fUF8KtNCD2ovwh3NYY8ip2AwBMSjtSflwc0YVH8taVPagcw0gUWwFbktwImNFCPNJlX8E7UPfyRkNZRj+G6dt/wDLVhh5h6UTYRH+Gadt/wDLUoxGur3OakR8sPtk0JJD1qWkgxQzplSOX9abCzWMUSIkiAHShWhbNS8sJG2KYNqcZwa0Qs+idSL+Xc9qElh5DhVZ3dgEUDPMfQVZbHRr3VZja2EKySEBizHZRv1/arnwr8Pjpt4NQ1R0muYyPCRN0U+tb+NVKT1mW6xLwhXw34Mbh3T3vb5E/il755Cpz4YP5R6fepTXo77UND1M2UAeaSIrbxMdixHXNFcT6zDounCe6kEUTypEXY4Cg9/6U1rfFnD3Cen/ADeqaraWlsuwZ5ASw7coHWupFYYX5Irgjh280fhmx0+/8O1WJedoYjh+Yk5yageI/iPc32pScI/Diyi1HVY/JcXg3ttOP+s9C3tmo19Q4o+MzNa6Ql3w5wgAFlv2UpdXq/yxj8q++TXRuGeFtF4P0pNK0KxjtLdPNgbtI38zHqx+9EUQfA/w8sOExNf3Vw+qa5dD/vOoTjLMfRf5R9jVyEbA+YdeppMMeW5skYXHTA+4p9+VtmAwPfFQnsTECV5gcA0zFOWkKOVLgZPLQUnEuni+gsYpkkuJXChFbp70RIY7W9QqN32/Wq3Cxd1dBYg6AnfB9qGgvVcZ3B96NMCv40eMA7j2oGW2z0q4kCEuVYgZp5SjAle/9aj0iK9qIjkKYDHYURDJ4OZg8YClTnaiGMXZuRzSI5ck5FKkt45hljhvUULRAW4ldCyTgg9nHeg7wRXYa1v7dZopPw2EgzsfepW4khER8dcoeuBULft8kYg7s9uWGC3Vf70Hkns8rX09z8KfiTxDaaJcOtrnk8DmwrxHOVJ/ShPEs7u6c2rkxSDnUE5IPpUn8c4ntviLfiNciWIPkdD12/rXOYdTaxaGaJiMbt/anxX2W0XhoF6oRlNwo35j6VDMy8O8RRGdB/CdYUxkMNlz/vVq08219Yx3kOCrjI5R0NA8SaZFr2hXemKo8VB41o5P+XjtTfkFqJSZ7c8EcVyaZfCR9POfC5jt4bdCf61GWca6XrM9gkiyxwvzoy7Aqe1H6tqg4u4Qt2uFzqWlkiZz1eMdAf61BzX3iSWd6EVIkBSR17+n7UqXkKPgucEq8qnO4WoueSW5uJljJDSHw8qdyPSiUkzbjkOS3Q07o0KLL4srKGU5Oex9axyTNcX4LHwRw3bQTI0nn5hyl26p9xV1v3s9FtRbWrrIxGX/ANNVO11Pwh4mUQ/lHTnPvUZc63JM7knBY7n29KVJjqiyXGrrMFaNsoowKjby/NuxfnDp6g1EDUFKlFHKPvQOpXwt4DzbFhn7UnNeM2PIxI7WNYlkuWSAkqDkjPSomXUJ7K5klt5Tg4znv1/vRVpbtMOfq0h327elZeabyDHLnbNaaljwyWSeaRs3Geq/TG5xQkmv3s7s8wVj+1auLX8Tw+UAmhJbaVJinKT7rvWhQSMneTDLfWpkfJOPaj31hrlgYQ5xscVER6XcshlJCIDjLDrVt4e4KdlS+lnQRM2eVehpM1FD6+xLaMirGJG5LmXGyE/QfWpuDStQubCWS0nSUs2Y1PQH0om24XDlZdMs5IpfyO+wX9Kl7PS7bR7aaMXLF5hzzhfzmlLx6Hx8+yLtTNaxzvdK8U+Qk8bbjvuP2o4hLSBo3fl8X6H6gD7/AMtEfOWbFm8KaVCgTzbZG/Un71HapxBbadZqZESGGM4GfNgen2qeysz7IXiO/lijRDJzGMhywPl2qMt+KbeOe4yoe3uhynB8ySff/eh77jnRvCe2ntBcqCWwo6n0zVUtrmK81eWW1j8NJTkqego8WC1I6bdwwXOm288PPzr5dzlmFRV3byO0fKnI7HHMDvip/SIeaxjV1ImIxkj8tROr3lvaXbRQMGnTuRsKGtNywKyaUdIRIGTUZZZSqps8ZG4YDP7daUwVZWkHLK4PP5zt+1MSS8kDhW5MnO2+KEaVpkAny7KMZ6VthHqYJPQ0apcMvNHdvG5XKgnbHpVk4G4ntbbx7NbSKG4uvzxbc7feqC7jnZWHMnp0rVvdPDdIyn8RPOnaraUt0KPj0dmvpLXTk+Z1zU0gPLlIk3P6+lRGnapq/GEt+ugXHyGkhuS4vJ93jHdYztv0qK4b+H0nHa/x/VtZPyLkiOJGy5PofSuk2Om2mlWcVhYWggs4TlUG/MfU+prk8vlxh/Wv2baaZT8sb4c4e03QN9PheS7b/MvLlueU/Y9qsluQeYuxbOPMfz+majooVBJIz6UfbnrnviuHZ3n7ZvhkVmEfx3wBb/EXR0VPDi16zQPZTv0uB/JIe/t6b1xDg/ivUvhrxcuotDLaeA/ymq2bjLFCcEH1PvXpC3PLgqSozkgHv7elUz4v8Bf9o7CXinS4VOqWMI/iFsu63lsOrD/6n71v4PJ7f9mfoycmvP7pHTkkhnjiurR1a1uFWaBwcryntT6ADoc1yf4AcUDV9BueGGm8WSxBm08SHzFCPMhHsfeurRMD0rm8un47WkaaZqUUwlTSqbVs0sMOtYxv2bKjNJC9aVzA5ra70toNGInXenEQCsXG9LXYUGFm171sDbpWKeu1Lzt0qNgDP6VvHtSilb5aoISoHpSuXIrfLSlG29UQQsYPWsK7U5itHp0otQIxyVgQDtTpG9ayvrSwtEhcdqbkUeC+1EDJFNSDEL1SQLZGWSj+Faaf/wDWrYQVlhvpOm//ALanVTLAdQe+K3Vy7PDEDSRE4I6etNeEMY/pVA134raxo+tT2i2UbJGxVYwuXc+wpNr8aZJJB8zpvhhen4Tbf0rt1/jLJRUoCXyEvBfTCrbHGablt1jiZp3EcSjJYnaoGD4k2WoR8kKcs56ZQ4/5Vy/4h8acWtM1heSJFahsweGNmHv6Vq434ycZbIGXIXXTtHw+43ik41bR4oPCtL1C8Zcbswz/AHG1diXGPYV4W0XjvUNI1nS9TuZs/JXSpIwG4Unf9Ole3rC+h1CCO4t5A8M0YlRwdmX1rsdFFYYG23oNxFw/ZcUaRcaVqCs1vcLhuU4I9CPtVG0P4B8HaHcC5nhvNWmhOUOoSmRF9MA10wb79u1NnB+oZ/XaoUNwQQwRCJFVEUYVFUKqD0AHQe1LVRzgjtW2IQEtSYWLAsBuOq56CoQRdM0cJMWSQvKo7feqg+u6jf3r28lm6WVuPxJyeXP9KtV7clVi5don8pc/kqPNvHclzDz3eBynJ/DJ9atZ9ja2uvkrcmhBzPrFtcRRSwEMgHUH0PpVpS8upNJtJruMLO2CwH5ap+raXqceoeHpyOwkHK/h7qR7ir1IRDYRmdD5FHMo3NFLGKDwAWLA7EUMw32pYl5UXAJ8uRTCTBuhzQVv2WaaPGd6Ty+gp8LnrSTyjpRIpCHcoOmK0khbrmlyzFCQqjA7kVEz6sLaeSGTytGObJ/N7CrLRLoynYqrD3obU7WO8s5FKFiMMMCmba7W6QNC3Nkbj0+9GRXHIpJJUqNx60Cwh5M/xA8jceWM8SzKZbU8zAZRT6GuXzxqfKB+td2/xI2TW2uWMEYC22oWzGMDqJd9s/pXCbVvGhZSpDwjw5c9ebvTo+itJngbiKS1kudJc4JOUJOwqbu9YCkPGcKucjua59es1jcx3aHlIblOO9HXOpNOpdm3NLxkQHNOlnrVy/Nyw3oPk7cx/wDZqFkRrYTQyOCnNlU7feitTl8Vw+MYOTUe0qvcc8vmV1x6VZCw8OamJ7RreRzzoNqm7a4FuHZgG7BT1qiWNyba6aQDGRirNb3ZmjVw45sbtSnEbGeErcanI0ZAGQPpXO9D/wAQKyheYkVDnU3XJUg5GDnrQ8F6zSdc/elyqTHQsLILxmI5W3BzTV4WvblYy2VU5NCWz+MxGAD96xg8jSiInITmf/T7e9IUMY7voa8zA4QeUfSfWmFuVmdwXA5TjJNAQyvdQKxk8NI9uYnqfSnYlRIJGQoS/d+xpqQuUt8BNvaiW+c/hyJnHWjYtKa5ZgkXhoehIqOt72G1TCt+IerdgaJHEEW6O0s0jAERw7g+tVLSRSRJ2mh2seIJRLO46DOVq26SssUaKkcY5eg5dh+lVjSU4j4is57vQ9IluLa3QrIYB51YZyMfpV6+Fvwj1z4iaTcaleajcaRCJeQRts5O+dtsdv3pTWhqxRH/AOImzjkkuNQiiiXdwGx4Y96j7bVv4tewaZo1pLLeXLAQLKhXm/1Z9Kv3DHwDjsOLntuIbkappixc9uObHO/+v1rsN3wZpMs9hdwWUNvPYMPCeJApC/y0SgBO79HD+Hvg/r+rcZPp3FsnLYRwLNzWxx4hP5c9qcvv8MazayHubyafSxeKkUIfJSE/mJr0Dc3VtbQvcXUsUSxgHnfA5fvvUZq/ElhpVr8zPdRrG68yNkESAe4/SpglSlI8mcbf4c7zhzV0hhvI3sGmMhlY4KQbdv5vagH4Q03T7GS7so3+WEvJCzHLSD+Y103iTWbzjfUnu7p3jtSOVFUkKn/U1A3YFxfRW6xr4MEZKqNhn7UxIfH15KjrGszaVp/ysMge8mXBGPoWqXLcO868zFn7vnrQl1rc76pezXGebxWjO/QDtTZm591GKdGCi9RmnPt4Dy58QknPtWPJkM7bA9KjxMy55jk5pcTZyeYn2P5abJlJYsHXClsg5OM4poSxsjMXw48/3HpntSITJLMLaC3nnuSeURIuWP2xXUOC/gZeXnh33FYewsx5xZIfxpB7+lZbuTCpa2Mpqk/aJv4PWkkPBUs00YVbq5JiyNwPUGrqYWVvKeZR36USYYokjhggSG2iHLFCgwEH+9bZMHNeYttdlnZI7EI9VgOsZXO1PxbYrYGeorYHpUDiEwtgAUbZXz2Vyk8SKxU7qRkMO4NR6nrilxbv1IHtSlsXoUknHDlGpWEnwl+MFne2Kf8AhWpzF7Zz9OX2cY++Diu8tLDHcP4ZzDIQ8Z9RXMPjHow1n4eXFxBGfm9DnSeI535CdyPttVp4R1n+N8I6HqHUvbAZz39K38iPy0qwyV/1biWhZVJ60vxMA1Gx3I77Uv5rOd8Vx3Bo1R8h4lAzS0kPrUetwM7mn45s9KU4lh6v/WnUNBxvnFEwtmhaC0IU7mnF32pkHc0tTjNLkCL5RW+WtBs9q2DkUvWQwCt4reKyr0hmfatEj0rKSR70WFiT1pSjbO37VrkO+aUNhigKNgb03KPwXp0UicYharBfoiNPH/hOm/8A7an1yM8pwR0prSx/4Tpmf/8AGojl5c/8qbXJ9/HsyLEvJR9QsbLQPipous3MCSWl9lGeToj+tXXiX4icF6PM9sYbK5uF6qIVIP61C/EzTLM8Lul3Khuyea3hU/iH7en3riwtYGEbueWVG3Ygt+5r3/Ai7KE37OZc/J26D4q8LOyibT7JEfO8cIziuXceXXD/ABBdXKW7CLT7gfguw3RqgJJIY7K4uFmBjikwMIQXJ7KKEubK6W9k0/5m2e4MPjhnH4apjp966EY4Il58FG1bT7vRrqbTr6M4lTlifGzrn6s16l/w08bLxFwKmlXEpa/0RhA6N9Rj7Ee1ef7e5s+IbD+B6vMuUz8rdMN45PU+1EfCPia5+FPxShj1jKW16ny00g+ll7OKCyJa37PbBlA2zgDoK0ADkgnGM/pURc63ZWVpJeX13DBZxr4gmZuq9jXmz4t/4k9R1l7jRuC+e1sR5ZL/ABh3/wDTSurLPUMV9a3fOLe6hnaM8rJG4Yqff0pM0zqFmXaUjLKO615C/wAMN/q03xSZPnLqS3+WZ7tXcsHf1NeswXkYt4quo+lj6elRxLDomjvoXaIq8MqZKHqG+1C6XoEVjK/LePJGTkR9AKD8MxyeJAXiY7nFER6lehQJYo5T6oKrCEyqJDnlCp7k1kiiSNl8RQW6nrUYuoysMmFR+lbiuypzyZ/WhxkDCgIVec+ReXIpkW7RPjFMtPLMDErqFJzsKRE8toTyu0kXfm3NSKwgcZABjvSFGayEpOodTkGlFfCOGI/SjIKCh9mXah77SLfVIgsq4lQYVh2omIFxlTmtGfwiQwNVpCFg0WXT4maEsJYtyP8AzBTct4JF8RCvTBycZPpU/wCOrA5bPp9qpnFlnPo4+Yt/Pbs2cDtSpPFoUVrw5d/iJEmq2On+AY0nsiJo5C3Vhnyj968/m7tNQ4gkOnFz4yc84I+l++B3r0lrWh6Zx1pQs9d8fwi/MrwnlZTXAuLOCH4B4zutPtA8lrIviWkj7M696Dj8yM24jZ0OEVJkLqlr49rJEVAYNzAk7VXVvHaJD69qtcdzDd26uw8jHBB6g1TLpPlrqWItsDkVuEC55eZSCd6GkYGIgjBQ7Vjy9d96Y58k5Gc0PXCh1GBZW7VK2spPMqnGRmoUPhcYo20kbZge2KovwGyiPkznf0pmPZqXColbOM07PHhG5RhqW0HEJsHMcuQTgDJ3q1aNDBJzHw/xJBgHO1UmxuMuRntg1atIuyvKGblLfl9KRJGitpjN/ok9k81qkAdfqx15j7VVptSlZWiAck7HIxy11G1KXbBZ3xKn+W460DrnB2naoRcqpguW6hfpb3NSL/YUqvtFI0rS7rUYZ7hIjILbaVB2T1xXoz4CfD7TbKW/TWLS3vI540ls5GG+D1Fc94LgteFb92mhNxbSDlkDDPOPSui8P8ZW2mXvi2pEUCjlVM45V9KXJaXGDZ1/gvhHS+Bp9Rg0SAra3jm5ON+Q77E/rVl02CCyad7SBo4Jm5sKuDzb52/b9q4DxRrfFuucVWuqcH63Fp8NrAF+XuG/DlPqw71FQ6N8TdT1g3t1x/HY3Exw3gt+Eo+2apLA1wpy8no/Wtf0rQLYX2q3ttYohJLSsAT9vWufzf4h+FLy6+Q4dF9rmoHaOGCI8rH0LdB9659Z/C7SLmdbriPUtX4mlViC15cf93V/tVzUaVolp8qlzpWl28hxGNPUK4X3PWi+RDIcLPZHTT8U8bpPY8VzwxaLIXa60+1Xzch6LzjcEUxd6fpfDWiQWYjuDYQkm1iunLuwPTf06Vl7x9pmmIINHiV2hOeZztL/AKm/tVWF5e8RagjXczNGDk/yoOwU9qHsF8cYhLXLraSyEYiLEqij9qrFzqnykk1wVIbBJwc4qwao6W8LRwOPEYYVcVVtVt8iVOdwSCD7f3psZJmeSOT8SRAandzR/RM3OPvQcVyVU87coG2ff0qb1eFLecpNysrMBsenX+1Rdzp9tFOfDLAIPMH7j1rRFmKXsb+Y5voOTVn4C4IuuNOILfTJ7r+HwSHmmlPXlz2FQbwKsgReRUYBlPTIrtH+HvSZ7l9S1yaICxjXli8QebnyOntvWTm2/FDsh/HjsvJ0Xhng7h7gmN4eHrACQeVrm5HPIT6qT9P9ak2iyVZ+ZmBzzM2T9s0WYzv13pp8V5Wd0rHsjsQSigBkBJpHhqeoohxkmkkVEw8BnHtTW470Sy0NLsaNNgLwYr46CnEfBocyBRk1oS75q+rYehEsMeoWepWUigi4sZ0APQnG1VX4O3cknw7gt2f8SyvZLZ19DVns5fxwpGVYMp37EVQ/hRKY9O4otubl8PWWf7Z710IRcqWmZJNfIdHNwM4zShc5qGku/Od6ciuwftXPnBjlInY5c7miom9DUHFc82eU0Zbzlu9ZpxwanpNRybdaNhOVG9RFtJzHepK2bbFZmQNU04tMRDI608tLkRDo70obCkAdaWBmlFG81maysqyzKSR70qkk1NIbyd81gOa1WDahKFikz/5LUoUmf/JaiKfoitPONJ0vbrb1M2FutsDcznLL1B3FA8PRq1lpRKliltkKO9H3kM2n8M6hICzTCGSQA74IG1dT8bSv8zBZI5DpK3F7x7xPqXEtyk988BjsYUbKW0Xr96pkDRLealpN9qg0qyaMyPOy5Zn7IB7771G/C3WJbrXNTu72Yl7mQs59d+n2orjS6EeuQ6wkFuy2Ugn5JBlBjGzD81e147xGGyJtuIBaadZcWPqtqNSZ/wCHR6W0e0cROPFZfX3xTuo6Q9vLH8NbfWdHu5dYcXT6u0g5o9/8tT6fqKck17XdJuLj4m6twXpU+n61AtlFAoBEfoQvrUcsU3AvDF1pOv8AApXVtamMmlXiNlwG+lVONjWtWCGgXiPh6+1/ic8MKmiWd3pFsEd1lCrcBe4x1JqIsr624u0qXhbXikGoW7H5K9O246KT6VJyHQOG+A30viHhLU7DjGQs1tO+eaQnuG/2qp3EGg2fCTNe2usW3EkcgHNLGyxlT3GR1oW99lk7xx8UtXueEbHgzVVkhvdPJFw//mr2A/c/vVN1aw/h+mWN/NeK0115hAg2RNuo7Hep+whj+IOmzaffypb6/YQ+JbyZwLhR2z60F8NeAdT+IOumzkEqWETCS+mkOAoGfKD2O/Sq3CHbf8MPC7aPw5ecSSoBdaiwFuepCV3GCVBGE6BRioDSre1sLK3tbWJY7e3jCRouwGO9GfMmMGlaWSxu+X85P3qIvTqtxLz2V2LcCmJtR5BnNRVxrPhNzDzD0zio5EFT3XHtmTJD8rdAdQ7YqOHxF4t09yt9w6ZFzktEOlKbimMTFeYrnrvS04lZgVLEq3bFD3RSGofjfpEc4i1Kxu7THXKHA/WrxoHHPD2vrnTtVglPaPIz/Wq7DBpWqqxurG1nRxghk3/eoi/+DnC+qM0lq0+mXGNnt3K7+u1TsFh1iJTCeaIc/uvTFAapb3yMtzZnxo0+pVO4rkS6d8TvhyGn0vUP+0emJ/w/z47+tTnC3x+0e/uhZcRWcuh3wIDLKmFY/wBPaq8siRcE1+6Gyq2fT3qaGp8vJDeLySOMq3ZvtQl1ZQaraPfaPcRO5XmHKcg1VTxNJbwy6dfoxkjbPm+qM98ULeMngus06x4ZzhT1Pf8AaonXr6CfQ7oSMeUrkCoWDiASSfJXcwRx9D9eeoziPXIl0/5a3PMzjOax3X9IPR9FTlMh7e4jjgVVIK427E/pUVx3w0OMOHWSPy6lp2bi3mP1BB1Denb1p6I5UZ796Mt7oAjmk8oJjORuc9c+1efpucLO52bId4dTytrbtourSSop8C5y3KVwFI9KgtRlE85mXo/SulfELRNSvtRm0xrdWvIb7w7aFMBnU/8AsVQ/+yOtrefInTbr5kNy+H4R/wCdetr5EXHZM4fxS1pIhDk9TWDvXVdB/wAO/FWqI0motBo8eMqbkjLfpml//pz4wFxyGC3MPPy+N4gxj1xmlvnUx/8AIJcWz9HKTjHX+lP2r8gwd+lehdC/w56JZXgm1nXP4jDHs9vbLykntvmqH8XeFLXh/jG4t7O2EGn3ChrZQM4/XvS6udXbLrBlz4soLWc+S4MIZu1FCRgyjPNkZ3oAfSxPr0p0TsuMnHKNq2LyLHLqLlbxY/K3fHepLTL9i/OWzJ6UHHOCpLjakqAi+JF1zmltBweMvNlqEcjEjI9Qe1WCxuVvbdkG+Rjcbiuc2l8j5Z8Zb0qesNQ8Mkpcn7UpxNHyJk9eG805w0M2VjOdxnH96bn1m01AMZITG/dl2z+lOQamJox47ZHbbrUbqOnxTKXhyObuO1UWpYPQ6xfWswa2umbl6D0qQTibUyphMhVAebGc/pVTMc1qXYHJp+PVCqkyA5Ix0pbGx5EswtY4nv2BSS5lUE52Jxn7UqLWTkq7szuMZk/97VUP4useNnIJAp+LWri4LoIl5MZJ749KBe/JauZaZdbs7Qx+K/NJnAiTfJqQHE2W+XVI4wV5kWPfB96olvIrT88iMjDYSPvirbw9w5DA/wA/FI7o24LNnf3qpYiJORJ6TPqF0TcX0IWRPpB7+9Iuk5VYH96nILbkTzHI7D0FOJYxP4mwHKMsxGc1K5eQZrwcQ4itSuocrx8g5weZjgDr/emnS3mnAkkZo4BkFV3Lfyn+9WLi6P8Ah2pTW9xEZYXOeY71WpomZBJDIFtv+K3et8fRzZp9geWBJFQCPnnkIVRzdB6V62+Hdn8lwHpEICKWXmchdydv7V5r4V0yC8vGuHU+GdlY9j616V+G8/zXCduvNnwJSg+3rXL/ACabxmvjrGTTJjPtQ86YBOOlHMNjnbNCzKfDJJrgteToKRHMv1U0T1oh1+qmGWqSGdhPLzA9qHuIx1okkAHemZj5N6OK/ZCLlPKSDTLS4Oxpy7OSxqOln5W3rVVHQZPCRtJws4ya538M75hrnGFu/lX5gyEZ75P9quFvdKJ1x3Brm3w+uCvH3EsJPllBJ/f/AK10aa30ZklJfIjpUkm4OeozSop2Bxmo55wSgz0FKgkLP1rLOvwM7FgtJeudxUlbsQcioC2kIqYsps1zroD65E1atvUpbNURafT1qVtmrnSQ0PhaiFahIRsRmio1wOtKekHlbIO1OqKbRdutOoNjQYwTOT3rOT3reKzFQrWIApJGacIpC9KjL3warK2Dmt0JZsbUmf8AympeKTNvC9FHyDL0DcOMsVjpXKuGNuBn0rehaj/EzqumyeKDHzRyNINjkdqHsLmOz0PTZJXCgQDzHYfvUdJdjTeLI5nuDDBcoBFEBs5PrWrjWSqikYvj7I81yrJwrr2sWYj8J4Llk5c74yd/6VY9OC61p12GUMCAeb39KM/xE8OtofFtvxDBA3y2qIkcpzt4m+/9aA4clXStKuHm6S5z2wK9rxLe9aemecSucPaTf8Y8QRcH3vEsukWasJEjdsRxuOmMmpeLRuMPiFxtLw2nGVrJccNkS2l3K/kkIOzKapHFzvPeGdGdPMSCrYb96e4Z4e0y54V1PX/+1UmnapYZQWobEsoz2Od63KRlki0Xp+IfxZ43bTmm0271nQOXk2UIxXv03zQnxm+InEPEt1b8OcR6TZ2V7pn/AMQYOkkg75Fc60jXNU0DUTqGmahcW94QfxEcgt9z3omwg1DjDiKO0e9MmoXsnmllbYk96LQQO0vGsriO+gZkMTnDdyPb29q9Q/DXWLO64Vkit7aK18VvEcqMGT3NcI47+GWr8DW0Vxfype21ySgmjGFU+3Wuq/AqfT9b4DmVp411Wym8NkZt/D9aCb+yjqsOoLa2YM5wV60AdfyzM30Hvmoi/knZwvmaMJzFlGRJ7ioO51Aq/wBTEf6RkUnuWWm712BoZCJKhLrWEMbefBHrVbu7+UglcqD61HzTT3UZXJxjOwpbm2QNl1ITXPMG2PTepnSLt5WUeIT96pcNvcwWcmoSQOLdTyjPVz/p9asegzwpGlxJKsMTHGZTykfpQLsUi+W11Jax+I2QnbO2al9O1tbqVhFJlAcAGoaG80ufTZJLe7juvBGSitk1W7K/j064F7LcLBaSHJJ6CiU3vkYjsEV7zqVUn33/AHqK4l4V4d4xtzDq2nROcgiaNcOD/wC8U1pV5Fc28dzDMjwv+ZDzZFGXV4lpnzjHbtmmxsSKbOcXHBnGnw0uJb7hXVZb7TweZbV25iq+nehJ/iaOKZ4o76x+X1OMcjMF5eY9wRXSBr8cbFlbw8985zVG48t9DjFvrqxxwX0L55RsJD60X/J6AA7tb281CG3jeUyL5n5FJ8Ffc1IylZecrKsiJ+b0+47VUdI+KXEnDYuDpjWSGZ+eQzoGMntntU5p/wAVNG1VhFxTp0ejXMmyapbL5CfRl/61h5vBnKGmvi8hRZIhGA2G1N8kyk/iAk9WxUg0KLGXjlWe3beOePdXX1phlXGUZXFecaa2J2V/Zaih/FHQb6+tNP1jR7WWa/hmCGOIZbb83rjpvXQxrF66QvNLF4xtk5yIgCG770GjSRMTHK6Hk+pDj/8AHNNsMDbenzuc4KP2gYQ6y0J8cysTISx9ySB9s9KIjdSPzH/8qiucgmiI5HzsazSiMSWEmshLZyOXoVx1HaqJ8a+HjrHD0GpwrzS2G2B1I9KuMMmQfak6tbi80yaJgWAXmC+tN4VvS9Cb4doYjyPenMoZQE598Y6Uw2CDkb1aOOdBbTLwmNMRyk8pqqO3nIO2K9nX5Ws4Mm0xaykLgmti4KnI6YximWIzWleqwtMKilWIo2S3tUnFKXUhD5h1qFUgeYHfFE2t4IZgS+AOpxQdQossum38oUhySqdTmpi2vVnjJz+gqpW2otKpwAATnAqYtAviqYWz6iluA2MtJjwI58gHB96S2miTCqwG+SSOlF2irdsWLKWHXlGKlI7XmTL/AL4pEvBorx+yCfSPEVDFDznmGRnpUpa8PsxZmiGMdB3PpU1ZWRg5SQcMMkAZzUzYr4Sc8aqwYd+7UrWOSRBaVwk8K+G4DGTcK4yy/cVabfTPkosBlCj6goyKSL6Q3BnmUZYYVh1z70TauY4yhHMwOAOxocC3BxoR5eXpgEn0rYlWGyu51KIW2UN+alySLPh3kXwx5WHrj0Peq9r2rQPp8iuGSOAcwfOPEo6o6xM5+CqcatDepJCgVJmAIHeqGlm13dpAiv4at+Io71YuIL+O7ik1GKVfoHIOrUJw9aNJbC7DuJJjggjGK27iwxpbLSy6LFHbKVC4Tm2x2rsfwnuG/h2pWJGWXzqewzXHtOijiOF8zM2Sa6X8KLy3ttUu7ae4SD5tAsbSfSW9Kw8tOUcRoh/VnSJSN/f+lDzfTvT86mNykilZF+oMME/Ydx70NI3MMdK4coNPya4tMFYYzTDjGaLdetCSdTS0sYaYO2M5oaaTc98U9K2M52xQMsoHMT0piWh6BXR+qoe7cHmxR9xKPPlqhbuZQSc10ONUxMpDcVzySp22/wCdc54NuGt/iPqigZ8Vip36b1eHm/HXlP5gK5zpF0tj8T7lWP8AmTkCupGORaMM5Lvp095d2OehpdtMS/WgZJyGYZ/Me1bt5MP1rLOHgNWFls5ASN6mrMYquWMuTttU9ZSHPrXKviaq3pPWh261J2zAVD2znAqVtCT3rlTia98EnCetGIdqAhP1b0bD0NK6MrQpfvS1yAdqaj3p9DuaBxaBMG9ZzVh3pJ2pfUpG84FIO1bLbU2Wqgja0oHOaSCBWs9aog8NzSZv8hqxT3pMrZhf2ol4I/RTtUuPmtD021LfgLB5sdPeom+1a64o0nS4tKhV5o5AkkoPmhx3/wCdRfFHE9vb6XY6Xpyu0ngDxW9SeoNAfDXUbvReILl7nKafeLykEbB+2/716XmcSKpyKMVD14zo/EfDVtxpwrPoM00VxdwxhoZM/TKP+VeZtU4intvGsrmHwru1cxTRsMAHsfsa7tDcNwbxeytLJNa6geYSNuA57VA/Gr4ZrxKjcZ8PQI99bry31svS4iH5l9T+lZvxnL6P45BXVYcAvXe/ZivNznsRgE+lQTwtHMJGTL+mdh/erdEY7m28pBYHGR+T2PvURrOnSJGXj29SBmvUQlLE2jBZEh7a0uNRn+WtYmkkZSx5euKXZ6hPot/bXqMDNZyB1C9x/tWtNv59Oufm7Cfwp0QgnGeYVuVLeeONo5C08o5pcjoacvQho71r2oRccfD6a0mdBFMnzNmqbkOBuK41wTrb6Dq0sL87pcjwpoxthqXwnxRc6LItpLdlbQSBkYjPK2d8exozjDRYY7iHXNMljuFkOZI4zgq3r71GtWFHTeH9c1DSLdlt71tW0mUZRJP86F/T7UfHxLbahJy3kTWcv5GA8g/Sud6dxPcSQeNNbLBKo5SY1xze9Fy8QXU2FJVQ3RsZpaoZC66tcOyeHZpBKWOFmLALUDezSQurQXkYmQ+YD6SPSoKS6eQcs8zAf+WNlrUVymCki7E5DZ6U6HG/YOkhc6ne3khmv7shF3jgj2VD6ih5bqWZJYZ2Lq55uUmmJbpJDlU5fbOaFkuGL77vjPN7elPjUkUmXP4Zarpmk6tcW9+VhgvIuSJmP0t71cLzTLXUbd7WNobi3L7AHy1xtpeZCrAHO4PcGlQ6le25HyF5NGR2Y4BrPbRvoPWX2bR9Z4KnGp6Le3r6Y55Z7cnmMX/pH71YdY4nMulJeQ65FKo28L8zH0rm0HHWv20hZLkS52aNxkH/AN71F3l013I0kkaRHm5lCDalx437K0vV7xtcWsBJm2I2U7mqlqGu3+uNmad+Xso7faop5ZZZFkc8xUdaWkM1vIrEjB9DmtVdXRECBfMoKN2G59aQbwtGV5Qobrk5z+9IMgcyZA9aYbffFNeP2ReC18K/EXVeEYZLMCK6s5jyxRzjPgn0+1WgfFdhG5uNIhWRMHw0G8gOd1/auR3kh8CYvIACMY5dsVqz1L5iIWtyzFhgRzL9SAZ2z+tZJ8Kub3B0b5R+zv3D/EOmcUwGSxJt2zymGU4Ib0o6a1miV/JvHu/+ketcIs5JoX54pn8LOfEU4P3PvVlm4skOkmGTULxZrlCGdPY1h/8AiY990cudP9HQDqGnsX8PULbKjYMetEcwjZUkIhd8EK5AJFcRkuo7e1iBYmfGRKf7U/ccRzXd2ly00qiMAAKSf61T/EQfpkj+Ql9ncIg0YZiCcdOXcGjLYP4zwsMl15V9j7+lcQ0jjrVLCS4Fhqj2sRP4ZuE5lLfy/wDX+lXLhL4x6XqF1b2Wu2b6Tfs2FlhHNFL7k7Yrm2/ipwl2ia4c5NeSl8Vx2uoRXdu7/wDeEuG2PUf+kVy68ilR2D/V6Cr18Q+IbOfjHU7q1Eq2EnkjmUdH7sB+1U+cu7HllV8dWz1/Su/Sn0SOba05eCJfIBIFaV9qfaFeXCIQ/vQ5XA2IP2poo2X9qUrsygHtTQZh1pxWBFDjC0dicB1zIUXOTjvUjYXczOxQlR05gdzUQNgM9KNtP/ivNIAq77GoEmi7adfLHIFiJ5SuXPofSrlYXcU9sMonKBnFcu/iscMe23iN2o/TOJpI7giXaH6ASevvWedOmiFmHToLmMLySSMG6Iex9s0S10gEYnDR9OVlOwPqaoGlcXcrvBNiSP6uY9jUxp3EcLpLiUSxkgcrHOKTKvDRG1Fxkuo0wS2QSd/5iMf3psXc8M2EzIjDAI7VWzxBax26zFizQAkDPXOP7VDw8XTGPzzGKJBn3pfRklYi0anxWthYmSGIM4JWSNh9I9R6VQ9b4kn1KEQpNi2MfKAuxT7+tRd/xDJdxzTRMCXc8xbqRUdpdlPqbSiFQYz5mJOMe1Prj1WmaT30S8QFzNbWiKvLAvM7j8/sas2nq2WEQCrnIGOlRul6dFaB0XJVV3Pep6zgI5fD+k/m7VUp6HXHAm15YWA5CW6nHYetZxHdnTeGbu/hyxgdShBwVJ70RblQpcnlbpnHb0oXjIl+D9WQ8vMQuABjp7VK1vsKzxHS8fBj4n6lxbz6NxFqltLM0WbKc45//SfWukvzRqyuOV1xzD0rx78PYJ4NUj1OLmVInAjI2LSHsK9eyOyxQCU80rwK8o6eb0rnc+nrJMvjz32ad+tCyEZO9bkkwCaGd8Ft65jjrNcfYzPIPNUTdy52zgUXPKEZg21Q93Nn2p1cApNICvpgOfBqEubrK4O5PvRl/MFJzUHPIgkO/wCldrjQ8GOyeD8UniSwtjH4grlt7dLb/EJ5VP0XWM10m1lYTJnzBMt6VyjPzvF5IPMZbwgGteGKUvOnYJjyyH7E0iBvP1pUoJkYe1ZFH/WkSj4LUiZsJcH3qwWTnOx61XbEVP2PbeuRyK2b6J+SwWjHAqZszmq/aSHpnpU7YHbNcz4/Jr7EpCD60bCcCgYW5sbYo2M4BqfED2C4j7U4vQ0xEw9KfX2pLqbC7Cs1ojNYD1rXNU/jsnYQwwCc02T/AEpwnrTRGxpMuM0EmhXNWc1Iyc1mTSfja+i/A5G1ak/yXpKnrW5D/wB3c1XRk+jhmkaWuLW5eRm/DBct3NRnHnFCLYvp9hhSdyyDcHtW73iBU062RDnli3Jqk31wb5y3Myk+hr3Moppr9nLXj0dU+HPFdj8SOGpOGNYcwavYj8OQHeQDuDUxw3xLqXDmpSWGsYghjzDB4m/ib/QB7158ihuNHuorzT3aC/gIKSA7ftXX9A4n0T4rRIuqXK2HEdvB4SgnCPg/WP8AVXB5/A6tTh6//DdTap+JBXxG+EUesSTcR8ERr8w295pqH6z/AKfeuKSXgZnt50a3mU4eCYYYfpXak4k1ngXULW11ebysxA5Thwv83uakNf0Tgj4oRJLqqtpmqSAtHfxLykj1I71fC/IyqfS3yv2Bbxd8xPMOoWamWR49nBwv2oJYJ+YKw5QepHeus69/h94r01Xn0ie21uzHmVoZMuV9cVSpODuK7Nis/D18h9WTpXoquXVYtg9Oe6ZL2OcK8KjV7z/xGT8CNC/IvUmlROHEzW4ZIoJPC5fSrfpNg3C2hyzXfL/EZYysa/y/eobTbIW0ssc55o7ok9O9bKZ9vozTWPwR8ZkOz/0o4cyKFK9KIFvCCeTr703IQDh9m9K0YQbZJD+Yv70nBVDzGlOfQlR3xWjysx5vpqwcRpWyNtqSh5kZj1zilooGDzA59KVIoPmWqBEL0zWmwVJByB7VvPMMCkhWwAMY7+9UGYh9utKyTjPb1pKSKrjNPsPmQxj6L1q8IMhhzcorcrHoO9LW3ZxkMgHuaSy8oOSCR6VCCE5g5OM5GMVjOFXJ2puW6jgQk5Mg7ChJDLIeY7J96HSDV07TZUjah4VWIYG3vRQwQaSVVegFTsQN0zUntpZIjhvmB36KPt61L2sy3Ng80LLNCfLIo2aI5/8AfSquFRQw5PqOetPwXM9tIswkJK/So2Cj2qaUOSSkTGC4D+IvRQtNiQyDkUlGPYVIT6pFqsKCRPDul3DIMlhQLN05gqsTgcvU1EWIlleYcjnyrsq42oYXUlpLHNGolMbeWM+n3p2VmGw6d6aKMAG3BIwPajxZhBGqX9tqUTr/AJbSsGxjaInr++1QT28cZwzssn8w6VLSweIGBbyNjmGOp+9RtxA9swVW5kIz06UvCDHLOpPMxI7GmhkdQB9hRKTMgZJRle1b5VfrQkAyynrSQxXtRDQLTLRMM7dKhWmi+RTkM4jJyOoxTNaGRQ4EGJctnc5HpTnzq8pBG3ffpQGWHQ1ivhskZ9RUwhJ291IWwXHIKxLx4jL4c5XPlAFRwkAyACB6ZpQaM/lOc9aFw0NSwl4tSmijZC+Q3qaaa5mnPIrkg9RQkXLJnJqTtmtIiDzYPrQOJFLQjSeHvGnAuNlPbFXPTrKCKErDGI4+mw6n0qt2uuWkC5OWde5FHx8Y8kYMccBAOcs3U+tV1bHV2KJZbWw5uaVD5D1GOtHMi2ilrgpbJ+VWYY/aqJc8ezTGQNciISDBWNc/1qGm4lmuJcRwyM3bmJIFUqP2W719HR5NesYOYCTxfTAxmoHX+KbG4tpLSYv4T4UqD5j75qnTz6jef5spUA52WmEt1jJLL4hY5JbrTY14Jne5LCf0bVZr3V9Gt4YvAtYbxTGqnr969e35RpsgHBiU7ivGujTNb6pppXcpcqxxXq/iDjHhjQjD/E9dtvEa2QlbRskfpXM51U5S8Ibx5xivITIxwQaDuDysfMD9jmqnqPxg4JsoPFEmo3TdsL1qp3nx8tObNvpsUNu3Qjdv+VY6+HY36NSvijoc83VZCN+m+9RF65A9/SoLQePpuIbVmvreA4/EieM7sv8ALjHX2qRmuBdjxYVZlYZx3Ap/8KcfZHdFkXqMpBODUQx796kb6G7LOPlLgEb45dzUTOs8BCy20sbHswxXS49bSMts0/Q/GQqSlj9MTHNcr4X/ABuLrPbGbkmulyy8ljeTcjlEt282O9c/+HlvK/FthiM/UW3GBTGmZpPTr7R5lY42yRTqRDetgHxHBBHmPUb4p1Bg0tpkHrUcq1NWTYIqGhyO1Sdq2AawXQbNNM8Jq3bB61O2Tjl61XrSQFvMce56D71MWcgXp5vtXPlQ19G1TJ63fpvR8R/Woi3kyD12qRt2J2zQyrYSkg+P23p1WOCRTET79KeVhgigjU/sLuh1TnNY39azmHbakluvrWmFGgdzRU70nlyOtKViazPLRPipk+QbxvSuTas6460rIrPPjf6LjMQO+1akP4DCnNjSZlxC1ZJcfBitPKl1dLcW1sFAAEf71FSW7qWIo8Ipt4DHuBHlj6e1DyE8pG+/evSGLAS4PODt1qv38MsEyy2zvE6EMrIcMP1qeIbpUfPB4jNnJqb9A4yz8PfFtTJHb8W2Cah4WFiuyvMyj3Hf96tsd9aa3qRvrK9gurLwikMWQpUfauNXOmZQ8qn3HagVae1kaSEy27H0yBWK/wDH12eUaYcmUFh3iO51SK5VNPvLi3z15G2A9MVrinjfULGyeGXUjJIowSTkmuTafxBrkSmRdSfkGd+pOPaoaXVWur4yyXLzMeoII/51OJ+MjF7oN3Icl6LZLqHzrtPJcGYN15tiBTFzctNCR4ix4yId98elQiTT5ZkiGD0PMOlbQvzc5XlB6b13a/6x8I5j1+yaF54q8yeXHWk/MHOWwzetRljMzCaFjh/qx6Cn1IUGQ7qoyaZGWrSg8PzAnG/f3rCNycUAJZc7GlreSA560elBUfQjFY/OF22oUXTscDanDK7KSTmoVg7zuOoH7UvmyOXl3oP5hwSAKSLl13yTQtlkgiuDnkQ49a27BWLCVEDHcelRsksjZ3P6UM8iu5DdPvU7EJJ72BDgfit7GmJb13B5FCZoNTliFwnuKUASwBOc1XYgsSl9zuaUKce2McPiY8ucU0DvihILUA9qxolO2MUuL6acZouUYzzE9PSoQElhEYyKSoz1oqcLyHLAAULzcnSjIJ8MRPzR+XkHMMVtSvMSwyHOfcUuNhIAnTlPNWmUCRjj7e1QghiQQWGAKTIxkJPYdBSjuCGOa0g2/wBqMgzy7e1NSQB1K9Sf6UW6IVwKSig9/MBk1RCFurRlVuYY9KFiJzirBdASbIA22cmoSdcOxRSMdqWQ0aQc0qNudeb1rfLnPtVFA7xj0pBjop09qZYe1QsZI3xSAuKdI8xpGahDMVmPetjesqEHEU4IFKAcNnNIVmB604o9TmphBUSFmIouLTQ/XfNNW+FYk0dFOoxjtUXgg5HpUK9aNhjjjHKFFCpOz07ExzmoUPMpKbgUJNb4BDfvRRkLDFNuOZSTvUIMWh8BjNzhfDwwJ9RUDPdyTXT3DktIzE5Jz+lTqRJJeW0dxzeCz4wD1qG1Gzaxu5YSNgcqfUVTiWNNeTnP4rDPYHamubPWlRRtNIscalnY4AFJwRt3zjHvVKOeiFz+H96/NdQ+JyrHiWPfBVvWr6uozwpMbd3ZTgnDYJ67/wBK5xwVbTRXkz4xlQmGHU+3qKtizJ4suCApIAx+Ub9T+tOreryV/wCixzcV608CwvOrxL9Mo+uhBrd9DLmW58WRenirzZNBzeHLYpOLlTk4ZOhT0+/ekK6c5IUrnrnuaJ4i/wD2WGHiidFJlhs5Inzzqq5H2p0ajaSHIs7S3I6SQJgiq7EqrGoePJbqQ3eiIbyNGQOoCgb47n1qYgdJ6O7kkJikuUEmNiV3J9K3BqDhjFLGu3WoBbiSGMtG2cNzBm60U97zcsisEcnDk78tT4ky9LKl7aDIcshHYiiIr+1Un8X+lVZLqTL+ODnPlY9GHqKIinUMA2N+9Klx0XGbRb4desbfc5kb+XsfvU5wjrejcU6wmji5FlLIC8TPsJMYyPvvXMJtTVXKqQMfmxQ3zGWjkU8skW8bpsUbbBH7UmXGTC+ZnqFeAJh/l6jgZyOZDkfcZoeXQNVtwS0SPlsAqcZrl/A/x11nRmS24nLarp30/NIMzg+47/vXY7P4k8Iarah4deshnYqz4ZD7jtWaXG/0HG1kSqtAxjmDo49V2p5CTmpmyv8AQ9VZo4NWtb5z0RXGf3pd1w/bKv8A3cOmdwqjP9aR/GwbG/SHzit83Xb+tP3emXdng8hmTGSydqEDRvnEi4HTerjTgxWpig3KCRWF89qbDZJG+3rSC2KNQK7Dqnr1rfMOxplXO9KDDFDOsuMx5TSpDmFs00r9dqW7fgtWWdYxSPJSpi3hCyEKycxGOvtTSmRlCl/IOlOQ8xtoC/8AJSSqHZTWnWUMyKFycUkLEwZguTT78vIRih+dkj261TZBHMg35MD3oS65JMhkDj0NESXBwQ2DQ5kK+bk5zjOBUj5BbS9nQPgDwTb8QcV3eoT26zWGnJlo3GQzHtj9665rHwn4P1GUvecMo2epgOD+1RPwE1HhbQOE0tZtbs49WvXMs6M2GUdlz7b12BYY7hRJGFdT0kRs5/avGflrOZG9yhqQdVkF7OHXf+Hjga5LNAL7TnHQNJn+lCf/AKYtCnOLPiy6jJ6Ax5x/Wu2XGmoXZ9/sBk0MbeWKZgjHC9tga51f5nm1+JSGumuXo838X/Ay94R4eueILXXxqSWT8lzahOXyZPmzv6elc0VgYjviOTzJ7ivYuqWTarJq+gTDyatZMYsEZLAHt+tePDEbNprSQDxbKZ7Vl/lCmvb/APT35GfLryftGHkVKv0aHMPrIz6A1nekhlUYBVq3zDFekb8+DKvXk0HGSFBz7UoSsrjfIpELKGJJwa2w9DRlablldckH+lDmaTtTz7g0M2R0pYRovKOrmtKx3yc0hmJrWcZqiD6n3p6Ns7+lCxtvREQPWoQkFk57Ro2OxbND46GkK+KUNxUKQtHJ27etOKwAYMAaZTyjGdvStg9eU5qFjgZWHLjP3piVBzZOBToDDc4rZ5WXcA0ZBm1wJMNvkdqXMuCwFaQAHKgg0uYEqDjfOahAY7dVpKA5p08xzzDB9K2q8+QSOb0oiDQUnoKbAIO3UHOaJcMqgqMnPShbo8jGFGBfq7dBGvqaBtkGnKSO8a58AeZyPzN7UiaEyHmbqRkEU9HGvKnICsKjZWG5HqaUEB6nb0oSETd2vLmaFdj9S+lDrlSQSKmnQZ2G3pUVdwLasJVU+Gf6VCDXNmtEZ7Uo4O46djTbc3aoQbZCSxFNGF99ulO5lGdq0JX3261CDIUr1Fb5TT3iA/VWB0PeoQbVMk43p1VbHSlRiPen08PeoQTFGxB3o63gwuCRn1pqLkIOKeXIFQg9EoDACs5jzYFIQnmyDTgHXkqEHEOOpp0BckE7etD8rYpyNcphlO1Qgh2zcREf8NsqfenL+1j1CKUEjnDEhz/N6UpFSRyikbb4xuT6CsiPNHIMeRgxx3DDrVryQrDymCfmiDoUGx6YPrRei2L6lqCQxwvcXEjckVvGMvNIegArJ0N1IvhjxJGPLhRnmPt613vhPhm0+BnCsvEGpLbzcb3sQ+WtpQH/AIajdC47Of6VWMhUeJeC4vhyljZXNwl7xRcRia9hVvw7GIj/ACx/qqMt41iiWNGLgHzEjr96bk1CTUpBfzl7q5mcyvNMfMzE9KJMy+AiwxEhupO2KOHgoJUfMSNJLEkyD6uUYye3+9KaRTEI8/j5zk7ChrdgnMCXwTk5p08sucMGJ6D0o8K02LjETL9BBxvSonKxeNs3m5cUkOUTwiUk5m32+mn7mNI5VjhyExzYPrULxAtzLNINtgKNiKCBvCfxk5POSMHNDTNiM48/PucVu3uQkZDIrFVx0xtV6Bg+kxlIVwxKjAGcgfaiHuWVeQOG9xUOLt5MgtygDI5aJhleZQzqAntVFoJLZ2I+/vWRkgZDAexpkOcb7n1rM81QmhUU5TIzjm2JHUe9Ow/Lycw8CBWXYsq4Lj39/eoszcjNg9B+1IE5IGCajwhLK8at4sBuYsfnt5Cpq5cH/F/i3hZ4omuV1jTl6wzZMxHpzZrn8MrAHB++aeWTLAg7jvQOKZE8PTHDPx74U1xRDes+k3ZGPAn6fvVsFjp+t2xvtIuYW8ToyMGT7HHQ14/D8+BIiOB6jf8AerLwJx3qPAGoi404mWwdgbmwBPK4/nXOcNSZ0hJs9C3NncWTcs8bLjudwfsaGKknqMHpUzwzxbonxC0n5rSZ45lGBJC+0kLehHahZ9G8J2WANFJjaKU/X9jS1HBqmRpwPWlhtt6SObmYFWRl6xMPMtaAIBIG1Rx0NSQ8v3pch/BamgcBiOlKLZiass4DYzR5UjkzaW5P8lMvyjdTg1uNl+UgHXyVrw4+XOd6UNGGfLHB2oeSR1zzbURcR8pJU7UE8sgcFMcv+qhLeDUr5YsP2qb4B4Wn454v0/QEV1jmc3FxIv5IPX/pUBykddx0J7Z+9dn/AMO+u8H8Fyalf8RapDZ6rdyEQiUnCw+mQK01RMtzLFrX+FlJWefReJJkkxgRmMLj9c1Tbr4RfFbgl2utMvriSFOkkF00j/8A8a9T6Xrmna3ALjTr+2uom6NE4JP6UYnLvyhVz6UyUIyX9kKUmvR5MtPjH8TuGARqsVzfoowTc2vhD/8AlUla/wCKMupW/wCELd2H1fLTeb9q9N3dhZ6hEYry0guY2/LKgYf1qjcTfAngPiZc3GiR2ch6y2Z8Nz+uKxS/G8ab1wQUbWck/wD1LcPDUrG7u+G7y2a3LAyLvhSPtXIONtX0TW+MdU1Ph2eQ6ZeHxuSZeVxITvt713LiD/CdpsNlNLofEd9byqCR80Q6qP8AeuTce/BbiT4d2EesX19Z6rpMuElmt1P4BJGMj9etaOHw6+O308aBOfYpRkV8MEA9hWLJmmQGxys42APlrYBro6wBwJlic1tm64rObl2pt5AAT1qdmTBfiAimHlDbqdqbSZuZs75ps8wbpVFii1IL1o/emj96hAhHzRMDnlBzUdG2CaNgOEHeoQKB96UsgHWkAjfakkZqihxZF5utLLkjIodRuaWgRpCsjFV9RVlhHPsOYisyehBFMkRc8ipkpzeXNOGUyMAaMgsAncHFbJbOM5GM57VuBQ6M3QA4we9aRSszcx8pXC+lQg0H5gSTvnAI7mlFVwrKcNWoYTCxjXzAbjPc1j4jTxT0XqPeiIJkl8LA/M2wFJhtgefyh3I82ejn+U+v3popLzeNL/mSjZMfStLUkLg5wOgBoCGhbtFEeZs9ixO+PTFN9qKhkUEnYPjB5txilrFEw2FCQDQBs+1altw6MjAFPt0osxqAQF61sP4aAYBYnz7VCFfksvCkEZ7/AEe9INo35G/pUzqVitwhU5R0BaAjufSq+LmaNiGDDHXbcGoQW1vOKaeFh1Qk+gpxNRJOMkfelx3CyyZY/sahAYRA9VIra2n+k0aJFXPKAfvS0umCkcqkDtioQESzY9EP6Cn47XOfIc+hpfzjr6j7ClLcPzc4LfYioQdhtQgOSOanDGFHUGmwJZsZAA9tqUsaR/Wf61CG/KOlLjG3f9qb8e3TZOfPuuadh8dgDHAzKe7HlqEFqHx5B+4pTr4cfiTycifzdqc+XllVg92Iv9IXNOxWfhIJjCAB+abeM/pVrPsgEpkdhycscJG8zbY91HelKrXMK/Lq8Ma5WFpNmkY9SfSm7y9tg+PFF1IRsirhFHtQbPc38qr4jeM+3LnYf2qiE1wnFNHr4uoWjiNgPFM5GVU+g9am9d1q84guCzhnRjzGZ2zJIf8AUe9R9nCmnWvycYOx5pM9C3qfX7U+pELM2ATGMijIM2KRiX5d8IDtExO3N6UeYWQMnJjlO++eWoy6TxFkUjJkPiL/AKWo21vJJ4Ypzs0o5WHUmppBQlxzBOYn3p7xhJuqrGyrgjPWmBKwkeRkB9ulahkyC5UBpNwDvRlYHOwjijYcgdhg460iW7UgKuebsT3ptHRIXZmG+2WG4PpTDMpOGBD9s1ZY5NzKmJpF5X3z6UiJgObwiWBHek+IrYRwpAPfetx+dXAwu/8AShANcjoCRjcdKdsCzDBY4HY7UNI7L5s7L9NP2isxLtvtREQcD19utazj3rUfKw8RgSh6gdaUwMpBgB+xqEGJh1wetNAhTjpTzo3Ixx9Jw3saYYZ7betVgWDkcp35jT0LfnVvLQnMCxAz0pwfSF5sAdqmEwOWQ9qdhYhfELEsMCgo5Bgrzb04jnHXoahCa0bV9Q0LU0v9LvnsrnZ2ZPpc+4rvvw9+MulcaMmjcQRpputAbKW8k/urYG/tXm5W9Tt3pXPHIpDk4VuYY28M+q9x+9JlWQ9j3tksSMbwNKkpGbiNMOB7+3vUDexx29ywIKwn6GxtXKvh18b9R4ckg03iqdr7SnUBbnHNLAP/AKnrXoOyn0zW9OjntHt7qzmUNG6bgikvYllNJcRksuCe/aks2Inx0FWHWdBhige4t25SoyyOdj/aqxNgRPzFkDAHPUfp60GNjYtHldEZIIM7eSksfesrKwmwblYMuKAdsscjI9Kysq0DJhFjaTXFzFBbr4kzyiJIuxB711/iH/DPfxW0LaJraXc0cQ5ra8UBeb2INZWVw/yXNtomlWwHFS9nK9X4W41+HVy8klnq2mSKeb5u0kZogPtVx4R/xOcbaMPC1OK24ntgd5W/DkH9Kysrs/juXPkQ2YmcEn4O0cKf4luBeJ3SCe+l0m8/NHeJyqD7N3/aunW2qW+pWoutOnivIT0eJwR+9ZWV0n4QpsHkvRI3hSFV8TKssgrnvHOlz8SfDPizQGYPNGjPD/6Bgjb2x1rKyqgyjxnaSh4I3bylwRt6g0sy8rdc1lZWgsUZ1I8TtTEk3O3l+msrKhBuNuUb0p5STgVlZUIN5NNSHrWVlQoTG2Wx60fbyFDtWVlQg/zZOaVmsrKhBSQvKWVBkqMsPQetJAzn7ZrKyoQ2vUDt2pSdDvWVlXpB6JlyJWQsUXlAH/Onnw8SN/xD1XtWVlEQ0kkTmVlYqVHftQqyNfr4zArGD5ARjPvWVlWQejbLln82dyfQ1ixqzc7Q8w9FNZWVeEBpUHmMcQRf5Qf96XE5jbY1lZSmQISQPncbUtYA/MTgE+prKyoQU9tJcoE8RUZMkE9qiNStSgN2xYSDyOAuw96ysqiAI+VnALNGzD8rbE0pbO2lzzQ2wx/JJmsrKshoaXbDPKsy/wDpNbGmIFOJLtSfVaysqENrpn/1rv8AUU6NOLA/jXO3XasrKhByPT4ekskpA/mOKUkFlCchbcn0L5rKyoUPx6hApKLzq3ZYkyTRCeO7OY7QsqDIeXyisrKv60tErpegatfRR3MyRW9vMcKhGJDUZxFod5YWxvfmGlsxIIpAx80LHOOYemx3rKyhRGQHyty6STJbyFIlBORjI33/AKVMabp4slyAGuJAGZuvKPWsrKshJqwWNidyvU+tMCR3XmzsetZWVaZBMqPs6nJTzfpWtPMcdwbSRsQ3f4sbfmDelZWURAvnaVyGHLJkjB2rQLAljuMVlZREHXYq5LlZGG+e2fWsmLs4VfMxGSwGaysoiDAjMnMw6DvT0ar4WWO5XlrKyhABADkhzsOlHwK6RnJH2BrKyiKH4mdGDKRn+lO+dPxQ3nHpWVlUHhkkLqeYhm5/M2PWhG2kYDp2FZWVCtEJzCXG3TFbAw2DWVlWEaZSMsGAPpTkUjdz16VlZUIERSpzYY4Huacix5uXdc4FZWVWECoZQrlD0YYOehHv61OcNcX69wlcGTQtRkiUkFraXeI/b071lZVdUQvl38fLvU9Lu9L1fQxbi7ha3NxbvzYJGM9qjOCPiRdaDapoPEkpvLJABa36jMhX0P8AfNZWUpRSLR//2Q==',
            'file_type': 'jpeg'
        }
    }

    update_response = client.post('/api/v1/public/user/update',
                                  data=json.dumps(payload),
                                  headers={
                                      'Authorization': f'Bearer {token}'
                                  },
                                  follow_redirects=True,
                                  content_type='application/json')

    updated_user = update_response.get_json()

    assert update_response.status_code == HTTPCodes.Success.value
    assert updated_user.get('address') == initial_user_address
    assert updated_user.get('username') == initial_user_address
    assert updated_user.get('profile_picture_url') != ''

