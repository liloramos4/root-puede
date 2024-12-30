import os
import shutil
import subprocess
import pexpect
import sys

def main():
    # 1) Verificar y eliminar carpeta 'freeroot' si existe
    if os.path.isdir("freeroot"):
        print("🗑️ La carpeta 'freeroot' ya existe. Eliminando...")
        shutil.rmtree("freeroot", ignore_errors=True)
        if not os.path.exists("freeroot"):
            print("✅ Carpeta 'freeroot' eliminada exitosamente.")
        else:
            print("❌ Error al eliminar la carpeta 'freeroot'.")
            return

    # 2) Clonar el repositorio
    print("🛠️ Clonando el repositorio freeroot...")
    try:
        subprocess.check_call(["git", "clone", "https://github.com/foxytouxxx/freeroot.git"])
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al clonar el repositorio freeroot. Código de salida: {e.returncode}")
        return

    # Entrar al directorio 'freeroot'
    try:
        os.chdir("freeroot")
    except Exception as e:
        print(f"❌ Error: No se pudo entrar al directorio freeroot. Detalle: {e}")
        return

    # 3) Verificar la arquitectura del sistema
    print("🔍 Verificando la arquitectura del sistema...")
    try:
        arch = subprocess.check_output(["uname", "-m"]).decode().strip()
        print(f"📌 Arquitectura detectada: {arch}")
    except Exception as e:
        print(f"❌ Error al detectar la arquitectura: {e}")
        return

    # Solo soporta x86_64 o aarch64
    if arch not in ["x86_64", "aarch64"]:
        print(f"❌ Arquitectura no soportada: {arch}.")
        return

    # 4) Configurar permisos de ejecución para root.sh
    print("🔧 Configurando permisos de ejecución para root.sh...")
    try:
        os.chmod("root.sh", 0o755)
        print("   ↳ Permisos configurados correctamente.")
    except Exception as e:
        print(f"❌ Error al configurar permisos: {e}")
        return

    # 5) Ejecutar 'root.sh' por primera vez y automatizar la respuesta 'YES'
    print("🔄 Ejecutando 'root.sh' por primera vez...")
    print("   ↳ Este proceso puede tardar varios minutos. Por favor, espera.")
    try:
        child = pexpect.spawn("bash root.sh", encoding="utf-8", timeout=600)
        child.logfile = sys.stdout  # Mostrar salida en tiempo real

        try:
            # Esperar la pregunta "Do you want to install Ubuntu? (YES/no): "
            child.expect(r"Do you want to install Ubuntu\? \(YES/no\): ", timeout=60)
            print("   ↳ Respondiendo 'YES' a la instalación de Ubuntu...")
            child.sendline("YES")
        except (pexpect.TIMEOUT, pexpect.EOF) as e:
            print("❌ Error durante la instalación de Ubuntu.")
            print("   ↳ Última salida recibida:")
            print(child.before)
            child.close()
            return

        try:
            # Esperar la finalización con "Mission Completed ! <----"
            child.expect(r"Mission Completed ! <----", timeout=600)
            print("   ↳ root.sh ha completado la instalación.")
        except (pexpect.TIMEOUT, pexpect.EOF) as e:
            print("❌ Error durante la finalización de root.sh.")
            print("   ↳ Última salida recibida:")
            print(child.before)
            child.close()
            return

        if child.isalive():
            child.close()
            print("   ↳ root.sh finalizado exitosamente.")
        else:
            print("   ↳ root.sh terminó inesperadamente.")

    except pexpect.ExceptionPexpect as e:
        print(f"❌ Error al ejecutar root.sh con pexpect: {e}")
        return

    # 6) Verificar si /bin/sh existe en 'freeroot'
    bin_sh_path = os.path.join("bin", "sh")
    if os.path.exists(bin_sh_path):
        print("✅ /bin/sh encontrado. Ubuntu instalado correctamente en proot.")
    else:
        print("❌ /bin/sh no encontrado. La instalación de Ubuntu pudo haber fallado.")
        return

    # 6.1) Comprobar la ruta real de proot dentro de 'freeroot'
    # Normalmente se instala en 'usr/local/bin/proot'
    proot_path = os.path.join(os.getcwd(), "usr/local/bin/proot")
    if not os.path.isfile(proot_path):
        print(f"❌ No se encontró proot en la ruta esperada: {proot_path}")
        print("   Verifica que 'root.sh' haya descargado correctamente el binario proot.")
        return

    # 7) Entrar a PRoot de forma interactiva, forzando locale=C
    print("🔑 Entrando a PRoot en modo interactivo, forzando locale=C.")

    # Crear un diccionario con las variables de entorno actuales
    # y forzar las locales a "C".
    locale_env = os.environ.copy()
    locale_env["LC_ALL"] = "C"
    locale_env["LANG"] = "C"
    locale_env["LANGUAGE"] = "C"

    try:
        subprocess.run([
            proot_path,          # Usamos la ruta absoluta a proot
            "--rootfs=.",
            "-0",
            "-w", "/root",
            "-b", "/dev",
            "-b", "/sys",
            "-b", "/proc",
            "-b", "/etc/resolv.conf",
            "--kill-on-exit",
            "bash", "-c", "cat /etc/shells && bash"
        ],
        check=True,
        env=locale_env  # Aplicar el diccionario con LC_ALL=C
        )
        print("✅ Comandos ejecutados exitosamente dentro de PRoot.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error inesperado al ejecutar comandos adicionales en PRoot: {e}")
        print(f"   ↳ Código de salida: {e.returncode}")
        return

    print("🎯 Instalación y configuración completadas exitosamente en proot.")

if __name__ == "__main__":
    main()
