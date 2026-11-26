#!/bin/sh
# Compila y firma la app de Eye AF de la cámara (Android 4.x, API 10) sin SDK de Android Studio.
#
# Toolchain: JDK 17 + android.jar (API 34) + build-tools 34. Localización por variables:
#   JAVA_HOME   por defecto ~/.local/jdk17
#   ANDROID_SDK por defecto /tmp/sdk       (platforms/android-34, build-tools/34.0.0)
#
# Uso: ./build.sh          compila y firma -> out/EyeAf.apk
#      ./build.sh core     sólo el núcleo Java puro + sus pruebas (sin Android)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
JAVA_HOME=${JAVA_HOME:-$HOME/.local/jdk17}
SDK=${ANDROID_SDK:-/tmp/sdk}
AJ=$SDK/platforms/android-34/android.jar
BT=$SDK/build-tools/34.0.0
JAVAC=$JAVA_HOME/bin/javac
JAVA=$JAVA_HOME/bin/java
CORE="$HERE/src/eyeaf/AfPoint.java $HERE/src/eyeaf/AfTracker.java $HERE/src/eyeaf/WebApiMsg.java $HERE/src/eyeaf/SelfTest.java"

cd "$HERE"
rm -rf out
mkdir -p out/core

echo "== núcleo Java puro (sin Android)"
$JAVAC -d out/core $CORE
$JAVA -cp out/core eyeaf.SelfTest

if [ "$1" = "core" ]; then
    exit 0
fi

echo "== app Android"
[ -f "$AJ" ] || { echo "falta $AJ (define ANDROID_SDK)"; exit 1; }
mkdir -p out/cls
$JAVAC -source 8 -target 8 -nowarn -cp "$AJ" -d out/cls "$HERE"/src/eyeaf/*.java

$JAVA -cp "$BT/lib/d8.jar" com.android.tools.r8.D8 --min-api 10 --lib "$AJ" --output out out/cls/eyeaf/*.class
"$BT/aapt" package -f -M "$HERE/AndroidManifest.xml" -I "$AJ" -F out/unsigned.apk
(cd out && jar uf unsigned.apk classes.dex)

if [ ! -f "$HERE/debug.keystore" ]; then
    "$JAVA_HOME/bin/keytool" -genkeypair -keystore "$HERE/debug.keystore" -storepass android \
        -keypass android -alias k -keyalg RSA -keysize 2048 -validity 9999 -dname CN=a -noprompt
fi
$JAVA -jar "$BT/lib/apksigner.jar" sign --ks "$HERE/debug.keystore" --ks-pass pass:android \
    --v1-signing-enabled true --v2-signing-enabled false --out out/EyeAf.apk out/unsigned.apk
ls -l out/EyeAf.apk
