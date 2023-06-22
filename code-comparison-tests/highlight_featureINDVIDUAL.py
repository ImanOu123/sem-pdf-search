def on_button_click(button, fileInfo=("", "")):
    global fileToClear
            
    foundPgNum = -1
    overallHighlight = False
            
    # if direct change from file to file, clear previous file
    clear_file()

    
    pdfDoc = fitz.open(fileInfo[0])        
    found = False

    # iterate through pages in file
    for pgNum in range(len(pdfDoc)):
            
        foundTxtLst = []
        page = pdfDoc[pgNum]
                
        contextLst = [line for line in fileInfo[1].split('\n') if line.strip() not in {"", "-", "/", "."}][1:-1]
                
        # highlight sections and open file
        blocks = page.get_text("dict")["blocks"]
                
        
        for blockIdx, block in enumerate(blocks): 
            # to highlight entire paragraph 
            paraHighlighted = False
            hangingLinesBBOX = []
                    
            # look for text block by line
            if block['type'] == 0:
                for i, line in enumerate(block['lines']):
                    text = ""
                    bbox = []
                    lineHighlighted = False
                             
                    for span in line['spans']:
                        # extract bbox and text of line
                        bbox.append(span['bbox'])
                        text = text + " " + span['text']
                            
                    # check if text corresponds to context in contextLst
                    for context in contextLst: 
                                         
                        if remove_punct(remove_non_ascii(context).replace(" ", "")) == remove_punct(remove_non_ascii(text).replace(" ", "")):
                            # save pg number of where context is found
                            if not found:
                                foundPgNum = pgNum + 1
                                found = True

                            # highlight found context in page, using bbox coords of first and last bbox of line
                            page.add_highlight_annot((bbox[0][0], bbox[0][1], bbox[-1][2], bbox[-1][3]))
                                    
                            # remove found context from context list
                            contextLst.remove(context)

                            paraHighlighted = True
                            lineHighlighted = True
                            overallHighlight = True
                                    
                            break

                            # if line is not highlighted than it is a hanging line
                            if not lineHighlighted:
                                hangingLinesBBOX.append((bbox[0][0], bbox[0][1], bbox[-1][2], bbox[-1][3]))
            
                            # check if last character in text is period and we have yet to actually highlight paragraph - 
                            # case: previous paragraph that shouldn't be highlighted in block
                            if text.replace(" ", "")[-1] in [".", "!", "?", ":"] and paraHighlighted == False and overallHighlight == False:
                                hangingLinesBBOX = []
                                
                            # check if last character in text is period - new paragraph 
                            # and we are no longer looking for context 
                            if text.replace(" ", "")[-1] in [".", "!", "?", ":"] and contextLst == [] and paraHighlighted == True:
                                paraHighlighted = False

                                for bboxHanging in hangingLinesBBOX:
                                    page.add_highlight_annot(bboxHanging)
                                
                                hangingLinesBBOX = []
                                
                            # if last line in block check if block was partially highlighted then highlight hanging lines
                            if i == (len(block['lines'])-1) and paraHighlighted == True:
                                for bbox in hangingLinesBBOX:
                                    page.add_highlight_annot(bbox)

                                # if there is a previous top hanging line highlight it - case: indented lines are considered 
                                # separate block
                                if blockIdx != 0 and blocks[blockIdx-1]['type'] == 0 and len(blocks[blockIdx-1]['lines']) == 1:
                                    topLineBbox = []
                                    
                                    for span in blocks[blockIdx-1]['lines'][0]['spans']:
                                        # extract bbox of top line
                                        topLineBbox.append(span['bbox'])
                                        
                                    page.add_highlight_annot((topLineBbox[0][0], topLineBbox[0][1], topLineBbox[-1][2], topLineBbox[-1][3]))
                            
            pdfDoc.save(fileInfo[0], incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            fileToClear = fileInfo[0]
            
            open_file(fileInfo[0], foundPgNum)