#!/bin/sh
# Compila y firma RemoteShutter con el toolchain de ~/.local/android-build (JDK17 + build-tools 34).
set -e
T=$HOME/.local/android-build; export JAVA_HOME=$(ls -d $T/jdk-17*); export PATH=$JAVA_HOME/bin:$PATH
BT=$(ls -d $T/android-*/ | head -1); AJ=$(ls $T/android-*/android.jar $T/platforms/*/android.jar 2>/dev/null | head -1)
cd "$(dirname "$0")"; rm -rf out && mkdir -p out/cls
javac -source 8 -target 8 -cp "$AJ" -d out/cls src/ar/shutter/*.java 2>&1 | grep -v warning || true
java -cp "$BT/lib/d8.jar" com.android.tools.r8.D8 --min-api 10 --lib "$AJ" --output out out/cls/ar/shutter/*.class
"$BT/aapt" package -f -M AndroidManifest.xml -I "$AJ" -F out/unsigned.apk
jar uf out/unsigned.apk -C out classes.dex
[ -f debug.keystore ] || keytool -genkeypair -keystore debug.keystore -storepass android -keypass android -alias k -keyalg RSA -keysize 2048 -validity 9999 -dname CN=a -noprompt
java -jar "$BT/lib/apksigner.jar" sign --ks debug.keystore --ks-pass pass:android --v1-signing-enabled true --v2-signing-enabled false --out out/RemoteShutter.apk out/unsigned.apk
ls -l out/RemoteShutter.apk
