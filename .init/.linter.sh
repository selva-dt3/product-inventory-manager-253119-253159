#!/bin/bash
cd /home/kavia/workspace/code-generation/product-inventory-manager-253119-253159/FastAPIBackend
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

