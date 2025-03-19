import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// Load the Flowscale CSS
const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = 'extensions/flowscale-nodes/web/css/emoji.css';
document.head.appendChild(link);

function setupFlowscaleNode(node, nodeData) {
    // Setup
}

function createVideoPreview(node, videoInfo) {
    // Remove existing preview if any
    const existingPreview = node.querySelector('.video-preview');
    if (existingPreview) {
        existingPreview.remove();
    }

    // Create video container
    const container = document.createElement('div');
    container.className = 'video-preview';
    container.style.cssText = 'margin: 10px; padding: 10px; border: 1px solid #666; border-radius: 4px;';

    // Create video element
    const video = document.createElement('video');
    video.style.cssText = 'width: 100%; max-height: 200px; border-radius: 2px;';
    video.controls = true;

    // Set video source based on type
    if (videoInfo.url.startsWith('file=')) {
        const filePath = videoInfo.url.substring(5);
        video.src = `/view/${encodeURIComponent(filePath)}`;
    } else {
        video.src = videoInfo.url;
    }

    // Add video info
    const info = document.createElement('div');
    info.style.cssText = 'margin-top: 5px; font-size: 12px; color: #aaa;';
    info.innerHTML = `
        <div>Filename: ${videoInfo.filename}</div>
        ${videoInfo.fps ? `<div>FPS: ${videoInfo.fps}</div>` : ''}
        ${videoInfo.total_frames ? `<div>Frames: ${videoInfo.total_frames}</div>` : ''}
        ${videoInfo.format ? `<div>Format: ${videoInfo.format}</div>` : ''}
    `;

    // Add elements to container
    container.appendChild(video);
    container.appendChild(info);

    // Add container to node
    node.appendChild(container);
}

function createImagePreview(node, imageInfo) {
    // Remove existing preview if any
    const existingPreview = node.querySelector('.image-preview');
    if (existingPreview) {
        existingPreview.remove();
    }

    // Create image container
    const container = document.createElement('div');
    container.className = 'image-preview';
    container.style.cssText = 'margin: 10px; padding: 10px; border: 1px solid #666; border-radius: 4px;';

    // Create image element
    const img = document.createElement('img');
    img.style.cssText = 'width: 100%; max-height: 200px; border-radius: 2px; object-fit: contain;';
    img.onerror = (e) => {
        console.error('Failed to load image:', imageInfo, e);
        img.alt = 'Failed to load image';
        img.style.height = '100px';
        img.style.background = '#333';
        img.style.display = 'flex';
        img.style.justifyContent = 'center';
        img.style.alignItems = 'center';
    };

    // Set image source using ComfyUI's standard view API format
    // The correct format is: /view?filename={filename}&subfolder={encodeURIComponent(imageInfo.subfolder)}&type={encodeURIComponent(imageInfo.type)}`;
    const imageUrl = `/view?filename=${encodeURIComponent(imageInfo.filename)}&subfolder=${encodeURIComponent(imageInfo.subfolder)}&type=${encodeURIComponent(imageInfo.type)}`;
    console.log('Image URL constructed:', imageUrl);
    img.src = imageUrl;

    // Add image info
    const info = document.createElement('div');
    info.style.cssText = 'margin-top: 5px; font-size: 12px; color: #aaa;';
    info.innerHTML = `
        <div>Filename: ${imageInfo.filename}</div>
        ${imageInfo.format ? `<div>Format: ${imageInfo.format}</div>` : ''}
    `;

    // Add elements to container
    container.appendChild(img);
    container.appendChild(info);

    // Add container to node
    node.appendChild(container);
}

function createAudioPreview(node, audioInfo) {
    // Remove existing preview if any
    const existingPreview = node.querySelector('.audio-preview');
    if (existingPreview) {
        existingPreview.remove();
    }

    // Create audio container
    const container = document.createElement('div');
    container.className = 'audio-preview';
    container.style.cssText = 'margin: 10px; padding: 10px; border: 1px solid #666; border-radius: 4px;';

    // Create audio element
    const audio = document.createElement('audio');
    audio.style.cssText = 'width: 100%; border-radius: 2px;';
    audio.controls = true;

    // Set audio source based on type
    if (audioInfo.url.startsWith('file=')) {
        const filePath = audioInfo.url.substring(5);
        audio.src = `/view/${encodeURIComponent(filePath)}`;
    } else {
        audio.src = audioInfo.url;
    }

    // Add audio info
    const info = document.createElement('div');
    info.style.cssText = 'margin-top: 5px; font-size: 12px; color: #aaa;';
    info.innerHTML = `
        <div>Filename: ${audioInfo.filename}</div>
        ${audioInfo.sample_rate ? `<div>Sample Rate: ${audioInfo.sample_rate} Hz</div>` : ''}
        ${audioInfo.channels ? `<div>Channels: ${audioInfo.channels}</div>` : ''}
        ${audioInfo.duration ? `<div>Duration: ${audioInfo.duration.toFixed(2)}s</div>` : ''}
    `;

    // Add elements to container
    container.appendChild(audio);
    container.appendChild(info);

    // Add container to node
    node.appendChild(container);
}

function createFileListPreview(node, fileList) {
    // Remove existing preview if any
    const existingPreview = node.querySelector('.file-list-preview');
    if (existingPreview) {
        existingPreview.remove();
    }

    if (!fileList || fileList.length === 0) return;

    // Create file list container
    const container = document.createElement('div');
    container.className = 'file-list-preview';
    container.style.cssText = 'margin: 10px; padding: 10px; border: 1px solid #666; border-radius: 4px; max-height: 200px; overflow-y: auto;';

    // Create file list
    const list = document.createElement('ul');
    list.style.cssText = 'list-style: none; padding: 0; margin: 0;';

    // Add files to the list
    fileList.forEach(file => {
        const item = document.createElement('li');
        item.style.cssText = 'padding: 4px 0; display: flex; justify-content: space-between; align-items: center;';

        // Get file extension for icon
        const ext = file.split('.').pop().toLowerCase();
        let icon = '📄'; // Default file icon
        
        // Set icon based on file extension
        if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext)) {
            icon = '🖼️';
        } else if (['mp4', 'webm', 'mkv', 'mov', 'avi'].includes(ext)) {
            icon = '🎬';
        } else if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) {
            icon = '🎵';
        } else if (['txt', 'md', 'json', 'csv', 'html', 'xml'].includes(ext)) {
            icon = '📝';
        } else if (['pdf'].includes(ext)) {
            icon = '📑';
        } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
            icon = '📦';
        }

        // File name with icon
        item.innerHTML = `${icon} ${file.split('/').pop()}`;
        
        // Add remove button
        const removeBtn = document.createElement('button');
        removeBtn.textContent = '✕';
        removeBtn.style.cssText = 'background: none; border: none; color: #999; cursor: pointer; font-weight: bold; padding: 2px 6px;';
        removeBtn.title = 'Remove file';
        removeBtn.onclick = (e) => {
            e.stopPropagation();
            // Get the current file list from the widget
            const widget = node.widgets.find(w => w.name === "file_list");
            if (widget) {
                try {
                    const files = JSON.parse(widget.value);
                    const updatedFiles = files.filter(f => f !== file);
                    widget.value = JSON.stringify(updatedFiles, null, 2);
                    
                    // Update the preview
                    createFileListPreview(node, updatedFiles);
                    
                    // Trigger the widget's callback if it exists
                    if (widget.callback) {
                        widget.callback(widget.value);
                    }
                } catch (err) {
                    console.error("Failed to parse file list:", err);
                }
            }
        };
        
        item.appendChild(removeBtn);
        list.appendChild(item);
    });

    // Add file count info
    const countInfo = document.createElement('div');
    countInfo.style.cssText = 'margin-top: 8px; font-size: 12px; color: #aaa;';
    countInfo.textContent = `${fileList.length} file${fileList.length !== 1 ? 's' : ''} selected`;

    // Add elements to container
    container.appendChild(list);
    container.appendChild(countInfo);

    // Add container to node
    node.appendChild(container);
}

async function uploadVideo(file) {
    try {
        // Wrap file in formdata so it includes filename
        const body = new FormData();
        const new_file = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
        });
        body.append("video", new_file);
        
        // Upload the file
        const resp = await api.fetchApi("/flowscale/io/upload", {
            method: "POST",
            body: body
        });

        if (resp.status === 200) {
            return resp;
        } else {
            alert(resp.status + " - " + resp.statusText);
        }
    } catch (error) {
        alert(error);
    }
}

async function uploadAudio(file) {
    try {
        // Reusing the video upload endpoint since it accepts any file
        const body = new FormData();
        const new_file = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
        });
        body.append("video", new_file);  // The endpoint uses "video" key but accepts audio files
        
        // Upload the file
        const resp = await api.fetchApi("/flowscale/io/upload", {
            method: "POST",
            body: body
        });

        if (resp.status === 200) {
            return await resp.json();
        } else {
            alert(resp.status + " - " + resp.statusText);
        }
    } catch (error) {
        alert(error);
    }
}

async function uploadFiles(files) {
    const uploadedFiles = [];
    
    try {
        for (const file of files) {
            // Wrap file in formdata so it includes filename
            const body = new FormData();
            const new_file = new File([file], file.name, {
                type: file.type,
                lastModified: file.lastModified,
            });
            body.append("video", new_file); // Reusing the video endpoint for all file types
            
            // Upload the file
            const resp = await api.fetchApi("/flowscale/io/upload", {
                method: "POST",
                body: body
            });

            if (resp.status === 200) {
                const data = await resp.json();
                // Add full path to the input directory
                uploadedFiles.push(`input/${data.filename}`);
            } else {
                console.error(`Error uploading ${file.name}: ${resp.status} - ${resp.statusText}`);
            }
        }
        
        return uploadedFiles;
    } catch (error) {
        console.error("Error uploading files:", error);
        return uploadedFiles;
    }
}

async function getVideoList() {
    try {
        const res = await api.fetchApi('/flowscale/io/list?directory=input');  // Changed from /fs/get_video_files
        if (res.status === 200) {
            const data = await res.json();
            // Filter for video files
            const videoFiles = data.directory_contents.filter(file => 
                file.toLowerCase().endsWith('.mp4') || 
                file.toLowerCase().endsWith('.webm') || 
                file.toLowerCase().endsWith('.gif') ||
                file.toLowerCase().endsWith('.mov') ||
                file.toLowerCase().endsWith('.avi') ||
                file.toLowerCase().endsWith('.mkv')
            );
            return videoFiles;
        }
        return [];
    } catch (error) {
        console.error("Error fetching video files:", error);
        return [];
    }
}

async function getAudioList() {
    try {
        const res = await api.fetchApi('/flowscale/io/list?directory=input');
        if (res.status === 200) {
            const data = await res.json();
            // Filter for audio files
            const audioFiles = data.directory_contents.filter(file => 
                file.toLowerCase().endsWith('.mp3') || 
                file.toLowerCase().endsWith('.wav') || 
                file.toLowerCase().endsWith('.ogg') ||
                file.toLowerCase().endsWith('.flac') ||
                file.toLowerCase().endsWith('.m4a') ||
                file.toLowerCase().endsWith('.aac')
            );
            return audioFiles;
        }
        return [];
    } catch (error) {
        console.error("Error fetching audio files:", error);
        return [];
    }
}

function addVideoUploadFeature(nodeType, nodeData) {
    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
        if (origOnNodeCreated) {
            origOnNodeCreated.apply(this, arguments);
        }

        // Add file input element for video upload
        const fileInput = document.createElement("input");
        Object.assign(fileInput, {
            type: "file",
            accept: "video/webm,video/mp4,video/x-matroska,image/gif",
            style: "display: none",
            onchange: async function() {
                if (fileInput.files.length) {
                    const file = fileInput.files[0];
                    await uploadVideo(file);
                    // Update the video list in the node
                    const videoWidget = this.widgets.find(w => w.name === "video");
                    if (videoWidget) {
                        // Refresh the widget's values
                        videoWidget.options.values = await getVideoList();
                        videoWidget.value = file.name;
                        if (videoWidget.callback) {
                            videoWidget.callback(file.name);
                        }
                    }
                }
            }.bind(this)
        });
        
        document.body.appendChild(fileInput);

        // Add upload button widget
        const uploadWidget = this.addWidget("button", "Upload Video", null, () => {
            fileInput.click();
        });
        uploadWidget.options.serialize = false;

        // Remove file input when node is removed
        const origOnRemoved = this.onRemoved;
        this.onRemoved = function() {
            fileInput.remove();
            if (origOnRemoved) {
                origOnRemoved.apply(this, arguments);
            }
        };
    };

    // Override onExecuted to handle video preview
    const origOnExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function(message) {
        if (origOnExecuted) {
            origOnExecuted.call(this, message);
        }

        // Handle video preview data
        if (message && message.ui && message.ui.video && message.ui.video.length > 0) {
            createVideoPreview(this.domElement, message.ui.video[0]);
        }
    };
}

function addAudioUploadFeature(nodeType, nodeData) {
    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
        if (origOnNodeCreated) {
            origOnNodeCreated.apply(this, arguments);
        }

        // Add file input element for audio upload
        const fileInput = document.createElement("input");
        Object.assign(fileInput, {
            type: "file",
            accept: "audio/wav,audio/mp3,audio/ogg,audio/flac,audio/mpeg,audio/aac",
            style: "display: none",
            onchange: async function() {
                if (fileInput.files.length) {
                    const file = fileInput.files[0];
                    const uploadResult = await uploadAudio(file);
                    
                    if (uploadResult) {
                        // Update the audio list in the node
                        const audioWidget = this.widgets.find(w => w.name === "audio");
                        if (audioWidget) {
                            // Refresh the widget's values
                            audioWidget.options.values = await getAudioList();
                            audioWidget.value = uploadResult.filename;
                            if (audioWidget.callback) {
                                audioWidget.callback(uploadResult.filename);
                            }
                        }
                    }
                }
            }.bind(this)
        });
        
        document.body.appendChild(fileInput);

        // Add upload button widget
        const uploadWidget = this.addWidget("button", "Upload Audio", null, () => {
            fileInput.click();
        });
        uploadWidget.options.serialize = false;

        // Remove file input when node is removed
        const origOnRemoved = this.onRemoved;
        this.onRemoved = function() {
            fileInput.remove();
            if (origOnRemoved) {
                origOnRemoved.apply(this, arguments);
            }
        };
    };

    // Override onExecuted to handle audio preview
    const origOnExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function(message) {
        if (origOnExecuted) {
            origOnExecuted.call(this, message);
        }

        // Handle audio preview data
        if (message && message.ui && message.ui.audio && message.ui.audio.length > 0) {
            createAudioPreview(this.domElement, message.ui.audio[0]);
        }
    };
}

function addMultiFileUploadFeature(nodeType, nodeData) {
    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
        if (origOnNodeCreated) {
            origOnNodeCreated.apply(this, arguments);
        }

        // Add file input element for multi-file upload
        const fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.accept = "*/*"; // Accept all file types
        fileInput.multiple = true; // Allow multiple file selection
        fileInput.style.display = "none";
        
        let uploadButtonWidget = null;
        
        // Create a safer file change handler
        const handleFileChange = async function() {
            if (!fileInput.files.length) return;
            
            // Get the upload button widget by name - do this here instead of closure
            uploadButtonWidget = this.widgets.find(w => w.name === "upload_files");
            
            // Store original text and update to show loading if button exists
            let originalText = "Upload Files";
            if (uploadButtonWidget) {
                originalText = uploadButtonWidget.name;
                uploadButtonWidget.name = "Uploading...";
                this.setDirtyCanvas(true, false);
            }
            
            try {
                // Upload files and get their paths
                const uploadedPaths = await uploadFiles(Array.from(fileInput.files));
                
                // Get the file_list widget
                const fileListWidget = this.widgets.find(w => w.name === "file_list");
                if (fileListWidget) {
                    let existingFiles = [];
                    try {
                        // Try to parse existing file list
                        existingFiles = JSON.parse(fileListWidget.value);
                        if (!Array.isArray(existingFiles)) {
                            existingFiles = [];
                        }
                    } catch (e) {
                        existingFiles = [];
                    }
                    
                    // Combine existing and new files
                    const updatedFiles = [...existingFiles, ...uploadedPaths];
                    
                    // Update the widget value
                    fileListWidget.value = JSON.stringify(updatedFiles, null, 2);
                    
                    // Create preview of files
                    createFileListPreview(this.domElement, updatedFiles);
                    
                    if (fileListWidget.callback) {
                        fileListWidget.callback(fileListWidget.value);
                    }
                }
            } catch (error) {
                console.error("Error uploading files:", error);
                alert("Some files failed to upload.");
            } finally {
                // Reset upload button safely
                if (uploadButtonWidget) {
                    uploadButtonWidget.name = originalText;
                    this.setDirtyCanvas(true, false);
                }
            }
        }.bind(this);
        
        // Assign the handler to the file input
        fileInput.onchange = handleFileChange;
        
        // Add file input to document
        document.body.appendChild(fileInput);

        // Add upload button widget
        uploadButtonWidget = this.addWidget("button", "Upload Files", "upload_files", () => {
            fileInput.click();
        });
        uploadButtonWidget.options.serialize = false;
        
        // Add clear button widget
        const clearWidget = this.addWidget("button", "Clear Files", "clear_files", () => {
            const fileListWidget = this.widgets.find(w => w.name === "file_list");
            if (fileListWidget) {
                fileListWidget.value = "[]";
                
                // Remove the preview
                const existingPreview = this.domElement.querySelector('.file-list-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                if (fileListWidget.callback) {
                    fileListWidget.callback(fileListWidget.value);
                }
            }
        });
        clearWidget.options.serialize = false;
        
        // Attempt to parse and display initial file list if present
        const fileListWidget = this.widgets.find(w => w.name === "file_list");
        if (fileListWidget && fileListWidget.value) {
            try {
                const fileList = JSON.parse(fileListWidget.value);
                if (Array.isArray(fileList) && fileList.length > 0) {
                    createFileListPreview(this.domElement, fileList);
                }
            } catch (e) {
                console.error("Error parsing initial file list:", e);
            }
        }

        // Remove file input when node is removed
        const origOnRemoved = this.onRemoved;
        this.onRemoved = function() {
            fileInput.remove();
            if (origOnRemoved) {
                origOnRemoved.apply(this, arguments);
            }
        };
    };
}

// Register extension 
app.registerExtension({
    name: "FlowScale.Core",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        console.log("Registering node type:", nodeType);
        console.log("Node data:", nodeData);
        
        // Apply Flowscale styling to all nodes that have our icon
        if (nodeData.name && nodeData.name.startsWith("FS")) {
            setupFlowscaleNode(nodeType, nodeData);
        }
        
        // Add upload features to specific nodes
        if (nodeData.name === "FSLoadVideo") {
            addVideoUploadFeature(nodeType, nodeData);
        }
        
        // Add audio upload feature to FSLoadAudio node
        if (nodeData.name === "FSLoadAudio") {
            addAudioUploadFeature(nodeType, nodeData);
        }
        
        // Add multi-file upload feature to MultiFileLoaderNode
        if (nodeData.name === "MultiFileLoaderNode") {
            addMultiFileUploadFeature(nodeType, nodeData);
        }
        
        // Add onExecuted handler for FSSaveImage to show image preview
        if (nodeData.name === "FSSaveImage") {
            const origOnExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                if (origOnExecuted) {
                    origOnExecuted.call(this, message);
                }
                
                // Debug logging
                console.log("FSSaveImage node executed, message received:", message);
                
                // Handle image preview data
                if (message && message.ui && message.ui.images && message.ui.images.length > 0) {
                    console.log("Creating image preview with:", message.ui.images[0]);
                    createImagePreview(this.domElement, message.ui.images[0]);
                } else {
                    console.log("No image preview data found in message");
                }
            };
        }
    }
});