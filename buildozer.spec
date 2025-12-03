[app]

title = ЧестныйЗнак
package.name = honestsign
package.domain = com.honestsign
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.2.1,requests,re

orientation = portrait
fullscreen = 0
android.permissions = INTERNET

# Важные настройки для новой версии
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 24

# Архитектура
android.arch = arm64-v8a, armeabi-v7a

# Отключить антивирусную проверку
android.antivirus = 0

# Пропустить проверку версий
p4a.allow_old_ndk = True

# Пути к SDK и NDK
android.sdk_path = %(android.sdk)s
android.ndk_path = %(android.ndk)s
