import pygame
import sys
import time
import threading
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import io
import urllib.request
import math
import random
import os
import ctypes

try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

# CONFIGURARE SPOTIFY CU DEVELOPER DASHBOARD
CLIENT_ID = "YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI = "http://127.0.0.1:8080/callback"
SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative"
# AUTENTIFICARE STANDARD
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE)
)

# INIMIOARE RANDOM
inimioare_fundal = []
for _ in range(50):
    hx = random.randint(20, 380)
    hy = random.randint(20, 680)
    dim = 10
    inimioare_fundal.append((hx, hy, dim))


# INTERFATA GRAFICA PYGAME 
pygame.init()
LATIME, INALTIME = 380, 680
ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption("With much love from Sebastian <3")
clock = pygame.time.Clock()
font_titlu = pygame.font.Font("Parisienne-Regular.ttf", 35)
font_artist = pygame.font.Font("Parisienne-Regular.ttf", 22)
font_butoane = pygame.font.SysFont("arial", 16, bold=True)
font_butoane_skip = pygame.font.Font("PixelifySans-VariableFont_wght.ttf", 20)

CULOARE_FUNDAL = (128, 0, 32)
CULOARE_TEXT = (255, 255, 255)
CULOARE_VERDE = (30, 215, 96)
CULOARE_GRI = (80, 80, 80)
CULOARE_ROSIE = (219, 112, 147)

date_playback = {"titlu": "Incarare...", "artist": "", "progres" : 0, "durata": 1000, "coperta_url": "", "is_playing": False, "volum": 50, "timp_volum": 0, "volum_salvat": 50}

# INITIALIZARE POZE CAMI SI SEBILE

folder_poze = "custom_images"
liste_poze_curente = []
index_poza_curenta = 0
DIM_POZA = 220

if os.path.exists(folder_poze):
    fisiere = sorted(os.listdir(folder_poze))
    for f in fisiere:
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            cale_img = os.path.join(folder_poze, f)
            img_surface = pygame.image.load(cale_img).convert()
            w, h = img_surface.get_size()
            dim_crop = min(w, h)
            x_crop = (w-dim_crop) // 2
            y_crop = (h-dim_crop) // 2
            img_crop = img_surface.subsurface(pygame.Rect(x_crop, y_crop, dim_crop, dim_crop))
            img_scaled = pygame.transform.scale(img_crop, (DIM_POZA, DIM_POZA))
            liste_poze_curente.append(img_scaled)

if not liste_poze_curente:
    surf_dummy = pygame.surface((DIM_POZA, DIM_POZA))
    surf_dummy.fill((50, 50, 50))
    liste_poze_curente.append(surf_dummy)

# PRELUARE PLAYLIST-URI
meniu_activ = False
lista_playlisturi = []
try:
    rezultat_pl = sp.current_user_playlists(limit=50)
    toate_pl = rezultat_pl['items']

    nume_vazute = set()
    for pl in toate_pl:
        if pl['uri'] not in nume_vazute:
            lista_playlisturi.append(pl)
            nume_vazute.add(pl['name'])
except Exception as e:
    print("Nu am putut extrage playlist-urile.")

# VARIABILE DE SCROLL
PL_ITEM_H = 30
PL_VISIBLE_H = PL_ITEM_H * 6
scroll_y = 0
total_pl_h = len(lista_playlisturi) * PL_ITEM_H
max_scroll_y = min(0, PL_VISIBLE_H - total_pl_h)

# FUNCTIE PENTRU COPERTA ALBUM
def incarca_coperta_de_pe_net(url, dimensiune=(220,220)):
    try:
        req = urllib.request.urlopen(url)
        date_imagine = req.read()
        imagine_raw = pygame.image.load(io.BytesIO(date_imagine))
        return pygame.transform.scale(imagine_raw, dimensiune)
    except Exception:
        suprafata_backup = pygame.Surface(dimensiune)
        suprafata_backup.fill((40,40,40))
        return suprafata_backup

def actualizeaza_date_bg():
    """Sincronizeaza datele in fundal la fiecare secunda"""
    global date_playback
    while True:
        try:
            current = sp.current_playback()
            if current and current.get('is_playing'):
                date_playback["is_playing"] = True
                item = current['item']
                date_playback["titlu"] = item['name']
                date_playback["artist"] = item['artists'][0]['name']
                date_playback["progres"] = current['progress_ms']
                date_playback["durata"] = item['duration_ms']
                date_playback["is_playing"] = current.get('is_playing', False)
                if time.time() - date_playback.get("timp_volum", 0) > 3.0:
                    date_playback["volum"] = current.get('device', {}).get('volume_percent', 50)

                if item.get("album") and item["album"]["images"]:
                    date_playback["coperta_url"] = item["album"]["images"][0]["url"]
                else:
                    date_playback["coperta_url"] = ""

            else:
                date_playback["titlu"] = "Pauza"
                date_playback["artist"] = ""
                date_playback["is_playing"] = False

        except Exception:
            pass
        time.sleep(1)

# PORNIM FIRUL DE EXECTUIE SECUNDAR PENTRU SINCRONIZARE
threading.Thread(target=actualizeaza_date_bg, daemon=True).start()

ultimul_url = ""
coperta_surface = None

running = True
timer_spotify = 0

while running:
    ecran.fill(CULOARE_FUNDAL)

    # DESENARE INIMIOARE RANDOM
    for hx, hy, dim in inimioare_fundal:
        puncte_inima = [
            (hx, hy + 10),
            (hx - 10, hy - 5),
            (hx - 10, hy - 10),
            (hx - 5, hy - 15),
            (hx, hy - 5),
            (hx + 5, hy - 15),
            (hx + 10, hy - 10),
            (hx + 10, hy - 5)
        ]
        pygame.draw.polygon(ecran, (80, 25, 45), puncte_inima)

    mx,my = pygame.mouse.get_pos()

    # DESENARE POZE
    # COORDONATE ZONA POZE (sus)
    POZA_X, POZA_Y = 30, 40
    
    ecran.blit(liste_poze_curente[index_poza_curenta], (POZA_X, POZA_Y))
    
    # CONTUR IN JURUL POZEI
    pygame.draw.rect(ecran, CULOARE_GRI, (POZA_X, POZA_Y, DIM_POZA, DIM_POZA), 1, border_radius=5)
    
    # SAGETI POZA
    btn_poza_stanga = pygame.Rect(POZA_X + 10, POZA_Y + (DIM_POZA // 2) -15, 30, 30)
    btn_poza_dreapta = pygame.Rect(POZA_X + DIM_POZA -40, POZA_Y + (DIM_POZA // 2) - 15, 30, 30)
    
    culoare_stanga = (80, 80, 80) if btn_poza_stanga.collidepoint(mx, my) else (30, 30, 30)
    culoare_dreapta = (80, 80, 80) if btn_poza_dreapta.collidepoint(mx, my) else (30, 30, 30)
    
    pygame.draw.rect(ecran, culoare_stanga, btn_poza_stanga, border_radius=5)
    pygame.draw.rect(ecran, culoare_dreapta, btn_poza_dreapta, border_radius=5)

    ecran.blit(font_butoane_skip.render("<", True, CULOARE_TEXT), (btn_poza_stanga.x + 8, btn_poza_stanga.y + 4))
    ecran.blit(font_butoane_skip.render(">", True, CULOARE_TEXT), (btn_poza_dreapta.x + 8, btn_poza_dreapta.y +4))

    # PENTRU A INCARCA COPERTA DOAR DACA S-A SCHIMBAT URL-UL

    if date_playback["coperta_url"] != ultimul_url:
        if date_playback["coperta_url"] != "":
            coperta_surface = incarca_coperta_de_pe_net(date_playback["coperta_url"], dimensiune=(220,220))
        else:
            coperta_surface = None
        ultimul_url = date_playback["coperta_url"]  

    # AFISARE COPERTA ALBUM
    if coperta_surface:
        ecran.blit(coperta_surface, (30, 275))

    # DACA TITLU E PREA MARE
    titlu_piesa =  date_playback['titlu']
    if len(titlu_piesa) > 20:
        titlu_piesa = titlu_piesa[:17] + "..."

    # Text titlu melodie
    text_titlu = font_titlu.render(f"{titlu_piesa}", True, CULOARE_TEXT)
    #x_centrat = (ecran.get_width() - text_titlu.get_width()) // 2
    ecran.blit(text_titlu, (30, 510))

    # Text artist
    text_artist = font_artist.render(f"{date_playback['artist']}", True, CULOARE_TEXT)
    #x_centrat_artist = (ecran.get_width() - text_artist.get_width()) // 2
    ecran.blit(text_artist, (30, 555))

    # BARA DE VOLUM CU HOVER SI CERC
    VOL_X, VOL_Y, VOL_W, VOL_H = 340, 275, 10, 200
    h_plin = int(VOL_H * (date_playback.get("volum", 50) / 100.0))
    y_plin = VOL_Y + VOL_H - h_plin

    hover_volum = VOL_X - 10 <= mx <= VOL_X + VOL_W + 10 and VOL_Y <= my <= VOL_Y + VOL_H
    if hover_volum:
        pygame.draw.rect(ecran, CULOARE_TEXT, (VOL_X - 2, VOL_Y - 2, VOL_W + 4, VOL_H + 4), border_radius=5, width=2)

    pygame.draw.rect(ecran, CULOARE_GRI, (VOL_X, VOL_Y, VOL_W, VOL_H), border_radius=5)
    pygame.draw.rect(ecran, CULOARE_VERDE, (VOL_X, y_plin, VOL_W, h_plin),border_radius=5)

    # CERC INDICATOR VOLUM
    x_cerc_vol = VOL_X + VOL_W // 2
    if hover_volum:
        pygame.draw.circle(ecran, CULOARE_TEXT, (x_cerc_vol, y_plin), 8)
        pygame.draw.circle(ecran, CULOARE_VERDE, (x_cerc_vol, y_plin), 6)
    else:
        pygame.draw.circle(ecran, CULOARE_TEXT, (x_cerc_vol, y_plin), 6)
        pygame.draw.circle(ecran, CULOARE_VERDE, (x_cerc_vol, y_plin), 4)


    # ICONITA DIFUZOR
    x_icon = VOL_X + (VOL_W // 2) - 6
    y_icon = VOL_Y + VOL_H + 18

    btn_mute = pygame.Rect(x_icon - 4, y_icon - 6, 24, 24)
    if btn_mute.collidepoint(mx, my):
        hx, hy = x_icon + 6, y_icon + 4
        heart_points = [
            (hx, hy + 12),
            (hx - 12, hy),
            (hx - 12, hy -6),
            (hx - 6, hy - 12),
            (hx, hy - 6),
            (hx + 6, hy - 12),
            (hx + 12, hy - 6),
            (hx + 12, hy)
        ]
        pygame.draw.polygon(ecran, CULOARE_TEXT, heart_points, 1)

    pygame.draw.rect(ecran, CULOARE_TEXT, (x_icon, y_icon + 3, 5, 6))
    pygame.draw.polygon(ecran, CULOARE_TEXT,[
        (x_icon + 5, y_icon + 3),
        (x_icon + 12, y_icon - 2),
        (x_icon + 12, y_icon + 14),
        (x_icon + 5, y_icon + 9)
    ])

    vol_curent = date_playback.get("volum", 50)

    if vol_curent == 0:
        pygame.draw.line(ecran, CULOARE_ROSIE, (x_icon + 2, y_icon - 2), (x_icon + 16, y_icon + 14), 2)
    else:
        rect_arc_1 = (x_icon + 8, y_icon + 2, 8, 8)
        pygame.draw.arc(ecran, CULOARE_TEXT, rect_arc_1, 0, math.pi/3, 1)
        pygame.draw.arc(ecran, CULOARE_TEXT, rect_arc_1, 5*math.pi/3, 2*math.pi, 1)

        if vol_curent > 33:
            rect_arc_2 = (x_icon + 4, y_icon - 2, 16, 16)
            pygame.draw.arc(ecran, CULOARE_TEXT, rect_arc_2, 0, math.pi/3, 1)
            pygame.draw.arc(ecran, CULOARE_TEXT, rect_arc_2, 5*math.pi/3, 2*math.pi, 1)

        if vol_curent > 66:
            rect_arc_3 = (x_icon, y_icon - 6, 24, 24)
            pygame.draw.arc(ecran, CULOARE_TEXT, rect_arc_3, 0, math.pi/3, 1)
            pygame.draw.arc(ecran, CULOARE_TEXT, rect_arc_3, 5*math.pi/3, 2*math.pi, 1)

    # BARA DE DERULARE (PROGRES) CU HOVER SI CERC
    
    BARA_X, BARA_Y, BARA_L, BARA_H = 27, 600, 300, 8

    durata_totala = date_playback.get("durata", 1000)
    if durata_totala == 0: durata_totala = 1
    proportie = min(date_playback.get("progres", 0) / durata_totala, 1.0)
    l_plina = int(BARA_L * proportie)

    # CONTUR HIGHLIGHT

    hover_progres = BARA_X <= mx <= BARA_X + BARA_L and BARA_Y - 5 <= my <= BARA_Y + BARA_H +5
    if hover_progres:
        pygame.draw.rect(ecran, CULOARE_TEXT, (BARA_X - 2, BARA_Y - 2, BARA_L + 4, BARA_H + 4), border_radius=5)

    pygame.draw.rect(ecran, CULOARE_GRI, (BARA_X, BARA_Y, BARA_L, BARA_H), border_radius=5)
    pygame.draw.rect(ecran, CULOARE_ROSIE, (BARA_X, BARA_Y, l_plina, BARA_H), border_radius=5)

    # CERC INDICATOR PROGRES
    x_cerc = BARA_X + l_plina
    y_cerc = BARA_Y + BARA_H // 2
    if hover_progres:
        pygame.draw.circle(ecran, CULOARE_TEXT, (x_cerc, y_cerc), 8)
        pygame.draw.circle(ecran, CULOARE_VERDE, (x_cerc, y_cerc), 6)
    else:
        pygame.draw.circle(ecran, CULOARE_TEXT, (x_cerc, y_cerc), 6)
        pygame.draw.circle(ecran, CULOARE_VERDE, (x_cerc, y_cerc), 4)


    # Butoane
    btn_prev = pygame.Rect(30, 625, 50, 40)
    btn_play = pygame.Rect(90, 625, 80, 40)
    btn_next = pygame.Rect(180, 625, 50, 40)

    # CULOARE BUTOANE PENTRU HOVER

    culoare_prev = (150, 150, 150) if btn_prev.collidepoint(mx,my) else CULOARE_GRI
    culoare_next = (150, 150, 150) if btn_next.collidepoint(mx,my) else CULOARE_GRI

    if date_playback.get("is_playing", False):
        text_play = "Stop"
        culoare_play = (240, 140, 170) if btn_play.collidepoint(mx,my) else CULOARE_ROSIE
    else:
        text_play = "Play<3"
        culoare_play = (50, 235, 116) if btn_play.collidepoint(mx,my) else CULOARE_VERDE

    pygame.draw.rect(ecran, culoare_prev, btn_prev, border_radius=8)
    pygame.draw.rect(ecran, culoare_play, btn_play, border_radius=8)
    pygame.draw.rect(ecran, culoare_next, btn_next, border_radius=8)

    x_centrat_prev = btn_prev.x + (btn_prev.width - font_butoane_skip.size("<-")[0]) // 2
    ecran.blit(font_butoane_skip.render("<-", True, CULOARE_TEXT), (x_centrat_prev, btn_prev.y +10))

    x_centrat_play = btn_play.x + (btn_play.width - font_butoane.size(text_play)[0]) // 2
    ecran.blit(font_butoane.render(text_play, True, CULOARE_TEXT), (x_centrat_play, btn_play.y +10))

    x_centrat_next = btn_next.x + (btn_next.width - font_butoane_skip.size("->")[0]) // 2
    ecran.blit(font_butoane_skip.render("->", True, CULOARE_TEXT), (x_centrat_next, btn_next.y +10))


    # DROPDOWN MENIU PLAYLIST
    
    BTN_DROP_X, BTN_DROP_Y, BTN_DROP_W, BTN_DROP_H = 30, 5, 220, 25

    hover_drop = BTN_DROP_X <= mx <= BTN_DROP_X + BTN_DROP_W and BTN_DROP_Y <= my <= BTN_DROP_Y + BTN_DROP_H
    culoare_btn_drop = (120, 120, 120) if hover_drop else CULOARE_GRI
    
    pygame.draw.rect(ecran, culoare_btn_drop, (BTN_DROP_X, BTN_DROP_Y, BTN_DROP_W, BTN_DROP_H), border_radius=4)
    text_btn = font_butoane.render("Chose your playlist", True, CULOARE_TEXT)
    ecran.blit(text_btn, (BTN_DROP_X + 10, BTN_DROP_Y + 4))

    if meniu_activ:
        start_index = abs(scroll_y) // PL_ITEM_H
        y_base = BTN_DROP_Y + BTN_DROP_H

        pygame.draw.rect(ecran, (40, 40, 40), (BTN_DROP_X, y_base, BTN_DROP_W, PL_VISIBLE_H), border_radius=4)
        pygame.draw.rect(ecran, CULOARE_TEXT, (BTN_DROP_X, y_base, BTN_DROP_W, PL_VISIBLE_H), 1, border_radius=4)

        for i in range(start_index, len(lista_playlisturi)):
            y_pl = y_base + scroll_y + i * PL_ITEM_H

            if y_pl < y_base or y_pl >= y_base + PL_VISIBLE_H:
                continue

            rect_item = pygame.Rect(BTN_DROP_X, y_pl, BTN_DROP_W, PL_ITEM_H)
            if rect_item.collidepoint(mx, my):
                pygame.draw.rect(ecran, (70, 70, 70), rect_item)

            nume_pl = lista_playlisturi[i]['name']
            if len(nume_pl) > 22: nume_pl = nume_pl[:19] + "..."
            ecran.blit(font_butoane_skip.render(nume_pl, True, CULOARE_TEXT), (BTN_DROP_X + 10, y_pl + 6))  

    # PRELUARE CLICK-URI
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEWHEEL:
            y_base = 5 + 25
            BTN_DROP_X, BTN_DROP_W = 30, 220
            if meniu_activ and BTN_DROP_X <= mx <= BTN_DROP_X + BTN_DROP_W and y_base <= my <= y_base + PL_VISIBLE_H:
                directie = 1 if event.y > 0 else -1
                scroll_y = max(max_scroll_y, min(0, scroll_y + event.y * PL_ITEM_H))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cx, cy = event.pos

            BTN_DROP_X, BTN_DROP_Y, BTN_DROP_W, BTN_DROP_H = 30, 5, 220, 25
            y_base = BTN_DROP_Y + BTN_DROP_H

            if BTN_DROP_X <= cx <= BTN_DROP_X + BTN_DROP_W and BTN_DROP_Y <= cy <= BTN_DROP_Y + BTN_DROP_H:
                meniu_activ = not meniu_activ
                if meniu_activ: scroll_y = 0

            # CLICK-URI IN INTERIORUL LISTEI
            elif meniu_activ and BTN_DROP_X <= cx <= BTN_DROP_X + BTN_DROP_W and y_base <= cy <= y_base + PL_VISIBLE_H:
                index_pl = (cy - y_base + abs(scroll_y)) // PL_ITEM_H
                if 0 <= index_pl < len(lista_playlisturi):
                    uri_playlist = lista_playlisturi[index_pl]['uri']
                    try: sp.start_playback(context_uri=uri_playlist)
                    except Exception: pass
                meniu_activ = False

            elif meniu_activ:
                meniu_activ = False

            if btn_play.collidepoint(cx, cy):
                try:
                    curr = sp.current_playback()
                    if curr and curr.get('is_playing'):
                        sp.pause_playback()
                    else:
                        sp.start_playback()
                except Exception:
                    pass
            elif btn_next.collidepoint(cx,cy):
                try:
                    sp.next_track()
                except Exception:
                    pass
            elif btn_prev.collidepoint(cx, cy):
                try:
                    sp.previous_track()
                except Exception:
                    pass

            # DERULARE LA SECUNDA FIXA CAND DAI CLICK OE BARA DE DERULARE
            elif BARA_X <= cx <= BARA_X + BARA_L and BARA_Y -5 <= cy <= BARA_Y + BARA_H + 5:
                rel_x = cx - BARA_X
                tinta_ms = int(date_playback["durata"] * (rel_x / BARA_L))
                try:
                    sp.seek_track(tinta_ms)
                except Exception:
                    pass

            # PENTRU BARA DE VOLUM
            elif VOL_X -10 <= cx <= VOL_X + VOL_W + 10 and VOL_Y <= cy <= VOL_Y + VOL_H:
                rel_y = cy - VOL_Y
                vol_nou = int((1-(rel_y / VOL_H)) * 100)
                vol_nou = max(0, min(100, vol_nou))
                try:
                    sp.volume(vol_nou)
                    date_playback["volum"] = vol_nou
                    date_playback["timp_volum"] = time.time()
                except Exception:
                    pass

            # PENTRU BUTONUL DE MUTE
            elif btn_mute.collidepoint(cx, cy):
                vol_curent = date_playback.get("volum", 50)

                if vol_curent > 0:
                    date_playback["volum_salvat"] = vol_curent
                    vol_nou = 0
                else:
                    vol_nou = date_playback.get("volum_salvat", 50)

                try:
                    sp.volume(vol_nou)
                    date_playback["volum"] = vol_nou
                    date_playback["timp_volum"] = time.time()
                except Exception:
                    pass

            # SCHIMBARE POZA
            elif btn_poza_stanga.collidepoint(cx, cy):
                index_poza_curenta = (index_poza_curenta - 1) % len(liste_poze_curente)
            elif btn_poza_dreapta.collidepoint(cx, cy):
                index_poza_curenta = (index_poza_curenta + 1) % len(liste_poze_curente)

    pygame.display.flip()
    clock.tick(15)

pygame.quit()
sys.exit()

