# -*- coding:utf-8 -*-
# папка для css файлов
import os.path

cBASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CICERO_PATH_TO_CSS = cBASE_DIR + "/css/"
#print "css = " + CICERO_PATH_TO_CSS

# Количество топиков и статей на одну страницу
CICERO_PAGINATE_BY = 16

# Директория с картинками -- частями мутантов. Внутри директории
# всевозможные части разделяются по поддиректориям:
#
# - arm-left
# - arm-right
# - body
# - head
# - leg-left
# - leg-right
#
# Если не указана, мутанты составляться не будут.
#CICERO_OPENID_MUTANT_PARTS = ''

# Оттенки, используемые в колоризации мутантов.
# Рекомендуется не менее четырех.
#CICERO_OPENID_MUTANT_COLORS = [
#    (0, 84, 102),
#    (102, 0, 0),
#    (43, 102, 0),
#    (102, 0, 102),
#]

# Фон для картинки мутанта. Если не задан (None), используется
# прозрачный фон (не работает в IE6).
#CICERO_OPENID_MUTANT_BACKGROUND = (255, 255, 255)

# Максимальный срок слежения за новыми непрочитанными статьями.
# Все статьи старше этого срока помечаются прочитанными.
# Задается в днях.
CICERO_UNREAD_TRACKING_PERIOD = 30

# Хост и порт поискового демона Sphinx
CICERO_SPHINX_SERVER = '127.0.0.1'
CICERO_SPHINX_PORT = 3312

# Число дней, после которых топики считаются "старыми" и статьи в них
# перестают попадать в новые.
CICERO_OLD_TOPIC_AGE = 60

#def is_user_can_add_topic_or_article(is_banned, ):