# Шрифты для PDF генерации

## DejaVu Fonts

Этот проект использует шрифты **DejaVu** для корректного отображения кириллицы в PDF документах.

### Лицензия

DejaVu Fonts License
https://dejavu-fonts.github.io/License.html

Шрифты DejaVu распространяются свободно и могут быть использованы в коммерческих проектах.

### Включённые шрифты

- `DejaVuSans.ttf` - основной шрифт (740 KB)
- `DejaVuSans-Bold.ttf` - жирный шрифт (690 KB)

### Источник

DejaVu Fonts версия 2.37
https://github.com/dejavu-fonts/dejavu-fonts

### Использование

Шрифты автоматически регистрируются в модуле `modules/pdf/fonts.py` при первой генерации PDF.

Если шрифты отсутствуют, система автоматически переключится на Helvetica (без поддержки кириллицы).
