import os
import pygame
import requests


def geo_search(search, ch=False):
    geocoder_request = \
        f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b" \
        f"&geocode={search}&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym = toponym["Point"]["pos"]
        if ch:
            ch = ''
        else:
            try:
                ch = json_response['response']['GeoObjectCollection']['featureMember'][0][
                    'GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['postal_code'] + '; '
            except Exception:
                ch = ('(Нет почтового кода); ')
        return toponym, \
               ch + json_response['response']['GeoObjectCollection']['featureMember'][0][
                   'GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
    else:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")


def exitt():
    try:
        os.remove('map.png')
    except Exception:
        pass
    exit()


def update(addr, pt):
    sp = {0: 'map', 1: 'sat', 2: 'sat,skl'}
    pos = [float(i) for i in geo_search(addr)[0].split(' ')]
    pos[0] += x
    pos[1] += y
    pos = ','.join([str(i) for i in pos])
    if pt:
        response = requests.get(
            f"http://static-maps.yandex.ru/1.x/?ll={pos}"
            f"&spn={scale},{scale}&l={sp[mapp]}&pt={','.join(pt.split(' '))},pm2am")
    else:
        response = requests.get(
            f"http://static-maps.yandex.ru/1.x/?ll={pos}"
            f"&spn={scale},{scale}&l={sp[mapp]}")
    if response:
        with open("map.png", "wb") as f:
            f.write(response.content)
    else:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        exitt()


def main():
    global scale, x, y, mapp, address, pt
    pygame.init()
    screen = pygame.display.set_mode((600, 610))
    pygame.display.set_caption('Большая задача по Maps API. Часть №10')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    font2 = pygame.font.Font(None, 18)
    input_box = pygame.Rect(10, 460, 300, 40)
    obj_addr = pygame.Rect(10, 510, 580, 40)
    pr1 = pygame.Rect(360, 560, 40, 40)
    pr2 = pygame.Rect(400, 560, 40, 40)
    pr_ch = False
    obj_addr_text = ''
    reset_button = pygame.Rect(10, 560, 335, 40)
    active = False
    text = 'Новосибирск'
    update(address, pt)
    while True:
        ch = False
        clock.tick(33)
        screen.fill(pygame.color.Color('white'))
        screen.blit(pygame.image.load("map.png"), (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitt()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    if 2 > scale > 0.3:
                        scale += 0.1
                        ch = True
                    elif scale < 0.3:
                        scale += 0.01
                        ch = True
                    elif 50 > scale > 2:
                        scale += 1
                        ch = True
                elif event.key == pygame.K_PAGEDOWN:
                    if 0.03 < scale < 0.5:
                        scale -= 0.01
                        ch = True
                    elif 0.03 > scale > 0.01:
                        scale -= 0.005
                        ch = True
                    elif 0.5 < scale < 2:
                        scale -= 0.05
                        ch = True
                    elif scale > 2:
                        scale -= 1
                        ch = True
                if event.key == pygame.K_UP:
                    if -90 <= y + scale <= 90:
                        y += scale
                        ch = True
                elif event.key == pygame.K_LEFT:
                    if -180 <= x - scale * 2 <= 180:
                        x -= scale * 2
                        ch = True
                elif event.key == pygame.K_DOWN:
                    if -90 <= y - scale <= 90:
                        y -= scale
                        ch = True
                elif event.key == pygame.K_RIGHT:
                    if -180 <= x + scale * 2 <= 180:
                        x += scale * 2
                        ch = True
                if event.key == pygame.K_q:
                    if not active:
                        if mapp == 2:
                            mapp = 0
                        else:
                            mapp += 1
                        ch = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                if reset_button.collidepoint(event.pos):
                    pt = None
                    ch = True
                    obj_addr_text = ''
                if pr1.collidepoint(event.pos) or pr2.collidepoint(event.pos):
                    pr_ch = not pr_ch
                    pt, obj_addr_text = geo_search(address, pr_ch)
                    ch = True
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        address = text.strip().replace(' ', ', ')
                        pt, obj_addr_text = geo_search(address, pr_ch)
                        x = y = 0
                        ch = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        if ch:
            update(address, pt)

        txt_surface = font.render(text, True, pygame.color.Color('black'))
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        if active:
            c = pygame.color.Color('red')
        else:
            c = pygame.color.Color('black')
        pygame.draw.rect(screen, c, input_box, 2)

        screen.blit(font2.render(obj_addr_text, True, pygame.color.Color('black')),
                    (obj_addr.x + 5, obj_addr.y + 5))
        pygame.draw.rect(screen, pygame.color.Color('black'), obj_addr, 2)

        screen.blit(font.render('Сброс поискового результата', True, pygame.color.Color('black')),
                    (reset_button.x + 5, reset_button.y + 5))
        pygame.draw.rect(screen, pygame.color.Color('black'), reset_button, 2)

        if not pr_ch:
            pygame.draw.rect(screen, pygame.color.Color('black'), pr1)
            pygame.draw.rect(screen, pygame.color.Color('black'), pr2, 2)
        else:
            pygame.draw.rect(screen, pygame.color.Color('black'), pr1, 2)
            pygame.draw.rect(screen, pygame.color.Color('black'), pr2)

        pygame.display.flip()


if __name__ == "__main__":
    pt = None
    x = y = 0
    mapp = 0
    address = 'Новосибирск'
    scale = 0.1
    main()

# Q - кнопка переключения слоев
# Для ввода нажать на текстовое поле в левой нижней области экрана
# Для поиска - нажать 'ENTER'
