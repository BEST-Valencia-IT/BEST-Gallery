# BEST Gallery
 
## Crear entorno virtual

```
python -m venv venv
```

### Windows

#### CMD

```
tutorial-env\Scripts\activate.bat
```

#### PowerShell

```
tutorial-env\Scripts\activate.bat
```

### Linux

```
source tutorial-env/bin/activate
```
### Instalación de dependencias
```
pip install requirements.txt
```

## Instrucciones desarrollo

Cuando se instale algún otro paquete de Python (mediante el uso de pip) habrá que actualizar *el requirements.txt* mediante este comando:
```
pip freeze > requirements.txt
```
**IMPORTANTE**: Si se instala algún paquete de Python todos deberán ejecutar también la instalación de dependencias de nuevo.