# LoRa-Vega-server-manager
Qt Python LoRa Vega server manager with GUI

This is a base program with GUI for communicating with LoRa Vega Network Server through websocket.
Vega Network Server is a tool for management of all-scale LoRaWAN® networks. 
Qt Python program communicates with Vega Network Server using Open API based on WebSocket/JSON technologies.
More information about Vega Network Server and its API you can find here:
[https://en.iotvega.com/product/server](https://en.iotvega.com/product/server)

If you need to migrate from PySide6 to PySide2 just rename "PySide6" to "PySide2" in imports and change the following lines at the end of main.py:

\# sys.exit(app.exec())  # PySide6
sys.exit(app.exec_())   # PySide2


![Qt Python LoRa Vega server manager with GUI](https://github.com/avanuser/LoRa-Vega-server-manager/blob/main/lora_vega_manager.png)
