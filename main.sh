#!/bin/bash

cd /c/Users/camara/Documents/feres/camaraNMS-20231005T143059Z-001/camaraNMS/client/.camaranms/
php last_sync.php
python api.py
python browserapi.py
