#!/usr/bin/env python

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28),
             ('.heap', 0x80, 0x1F),
             ('.stack', 0xC0, 0x22),
            ]

def procesar(segmentos, reqs, marcos_libres):
    resultados = []
    asignaciones = {}
    cola_fifo = []
    
    tamano_pagina = 0x10
    
    for req in reqs:
        offset_pagina = pagina_virtual = 0
        segmento_valido = False
        for _, base, limite in segmentos:
            if base <= req < base + limite:
                segmento_valido = True
                offset = req - base
                pagina_virtual = (base + (offset // tamano_pagina) * tamano_pagina)
                offset_pagina = offset % tamano_pagina
                break
        
        if not segmento_valido:
            resultados.append((req, 0x1ff, "Segmentation Fault"))
            continue
        
        if pagina_virtual in asignaciones:
            marco = asignaciones[pagina_virtual]
            dir_fisica = (marco * tamano_pagina) + offset_pagina
            resultados.append((req, dir_fisica, "Marco ya estaba asignado"))
            continue
        
        if marcos_libres:
            marco = marcos_libres.pop(0)
            asignaciones[pagina_virtual] = marco
            cola_fifo.append(pagina_virtual)  # Agregar a la cola FIFO
            dir_fisica = (marco * tamano_pagina) + offset_pagina
            resultados.append((req, dir_fisica, "Marco libre asignado"))
        else:
            pagina_a_reemplazar = cola_fifo.pop(0)
            marco = asignaciones[pagina_a_reemplazar]
            
            del asignaciones[pagina_a_reemplazar]
            
            asignaciones[pagina_virtual] = marco
            cola_fifo.append(pagina_virtual)  # Agregar a la cola FIFO
            
            dir_fisica = (marco * tamano_pagina) + offset_pagina
            resultados.append((req, dir_fisica, "Marco asignado"))
    
    return resultados

def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

