# Visualización de Diagramas

## 🔍 Cómo Ver los Diagramas Mermaid

Los diagramas en este proyecto están escritos en **Mermaid**, un lenguaje de diagramas que puede ser renderizado de varias maneras:

### Opción 1: VS Code (Recomendado)
Instala la extensión **Mermaid Preview** en VS Code:
1. Abre VS Code
2. Ve a Extensions (Ctrl+Shift+X)
3. Busca "Mermaid Preview"
4. Instala la extensión
5. Abre cualquier archivo `.md` con diagramas
6. Usa `Ctrl+Shift+V` para preview o `Ctrl+K V` para vista lado a lado

### Opción 2: Editor Online
Usa el editor oficial de Mermaid:
- **URL**: https://mermaid.live/
- Copia y pega el código Mermaid del archivo
- Visualiza y exporta como imagen

### Opción 3: GitHub (Limitado)
GitHub renderiza algunos diagramas Mermaid automáticamente, pero no todos. Para mejor compatibilidad, usa las opciones anteriores.

### Opción 4: Exportar como Imagen
Puedes generar imágenes PNG/SVG usando:
```bash
# Instalar mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generar imagen
mmdc -i diagrama.md -o diagrama.png
```

## 📁 Archivos con Diagramas

- **[Arquitectura del Sistema](arquitectura-sistema.md)** - Componentes principales
- **[Flujo de Secuencia](flujo-secuencia.md)** - Timing crítico de reservas  
- **[Plan de Implementación](../07-plan-implementacion.md)** - Gantt de desarrollo
- **[Flujo de Aplicación](../04-flujo-aplicacion.md)** - Diagramas de flujo detallados

## 🛠️ Herramientas Recomendadas

### Para Desarrollo
- **VS Code** + Mermaid Preview Extension
- **IntelliJ IDEA** + Mermaid Plugin
- **Obsidian** (soporte nativo)

### Para Documentación
- **Mermaid Live Editor** (https://mermaid.live/)
- **Draw.io** (para diagramas alternativos)
- **Excalidraw** (para sketches rápidos)

---

**Nota**: Si tienes problemas visualizando los diagramas, usa VS Code con la extensión Mermaid Preview para la mejor experiencia.
