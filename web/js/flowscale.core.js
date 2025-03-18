import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// Load the Flowscale CSS
const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = 'extensions/flowscale-nodes/web/css/emoji.css';
document.head.appendChild(link);

// Register audioUIWidget to handle audio previews
app.registerExtension({
    name: "FlowScale.AudioWidget",
    init() {
        // Create the audio UI widget
        const audioUIWidget = {
            name: "audioUIWidget",
            
            // Create DOM elements for the widget
            createElement(data) {
                // Only create audio preview if we have audio data
                if (!data || !Array.isArray(data.audio) || data.audio.length === 0) {
                    return null;
                }
                
                // Create container
                const container = document.createElement('div');
                container.className = 'audio-preview-container';
                container.style.cssText = 'padding: 10px; display: flex; flex-direction: column; gap: 10px;';
                
                // Process each audio item
                for (const audioInfo of data.audio) {
                    const audioElement = document.createElement('div');
                    audioElement.className = 'audio-preview';
                    audioElement.style.cssText = 'background: rgba(0, 0, 0, 0.2); border-radius: 8px; padding: 10px; margin-top: 5px;';
                    
                    // Create audio player
                    const audioPlayer = document.createElement('audio');
                    audioPlayer.controls = true;
                    audioPlayer.style.cssText = 'width: 100%;';
                    
                    // Set source
                    if (audioInfo.url) {
                        if (audioInfo.url.startsWith('file=')) {
                            const filePath = audioInfo.url.substring(5);
                            audioPlayer.src = `/view/${encodeURIComponent(filePath)}`;
                        } else {
                            audioPlayer.src = audioInfo.url;
                        }
                    } else if (audioInfo.filename) {
                        // Construct path for saved files
                        const subfolder = audioInfo.subfolder || '';
                        const path = subfolder ? `${subfolder}/${audioInfo.filename}` : audioInfo.filename;
                        audioPlayer.src = `/api/outputs/${encodeURIComponent(path)}?t=${Date.now()}`;
                    }
                    
                    // Create info display
                    const infoDiv = document.createElement('div');
                    infoDiv.style.cssText = 'margin-top: 5px; font-size: 12px; color: #aaa;';
                    
                    // Populate info
                    const filename = audioInfo.filename || 'audio';
                    let infoText = `<div>File: ${filename}</div>`;
                    
                    if (audioInfo.sample_rate) {
                        infoText += `<div>Sample rate: ${audioInfo.sample_rate} Hz</div>`;
                    }
                    if (audioInfo.channels) {
                        infoText += `<div>Channels: ${audioInfo.channels}</div>`;
                    }
                    if (audioInfo.operation) {
                        infoText += `<div>Process: ${audioInfo.operation}</div>`;
                    }
                    if (audioInfo.format) {
                        infoText += `<div>Format: ${audioInfo.format}</div>`;
                    }
                    
                    infoDiv.innerHTML = infoText;
                    
                    // Add elements to the audio preview
                    audioElement.appendChild(audioPlayer);
                    audioElement.appendChild(infoDiv);
                    
                    // Add to container
                    container.appendChild(audioElement);
                }
                
                return container;
            },
            
            // Update existing elements or create new ones
            update(element, data) {
                if (element) {
                    // Remove existing content
                    while (element.firstChild) {
                        element.removeChild(element.firstChild);
                    }
                }
                
                // Create new elements
                const newElement = this.createElement(data);
                if (!element && !newElement) return null;
                
                if (!element && newElement) {
                    return newElement;
                }
                
                if (element && !newElement) {
                    element.remove();
                    return null;
                }
                
                // Copy children from new element to existing element
                while (newElement.firstChild) {
                    element.appendChild(newElement.firstChild);
                }
                
                return element;
            }
        };
        
        // Register the audio UI widget
        app.ui.imagePreviewWidget.registerWidget(audioUIWidget);
    }
});

// Override node title handling
function setupFlowscaleNode(node, nodeData) {
    // ...existing code...
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
        ${audioInfo.format ? `<div>Format: ${audioInfo.format}</div>` : ''}
    `;

    // Add elements to container
    container.appendChild(audio);
    container.appendChild(info);

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
        // Wrap file in formdata so it includes filename
        const body = new FormData();
        const new_file = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
        });
        body.append("audio", new_file);
        
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
        const res = await api.fetchApi('/flowscale/io/list?directory=input');  // Changed from /fs/get_audio_files
        if (res.status === 200) {
            const data = await res.json();
            // Filter for audio files
            const audioFiles = data.directory_contents.filter(file => 
                file.toLowerCase().endsWith('.mp3') || 
                file.toLowerCase().endsWith('.wav') || 
                file.toLowerCase().endsWith('.ogg') ||
                file.toLowerCase().endsWith('.flac') ||
                file.toLowerCase().endsWith('.aac') ||
                file.toLowerCase().endsWith('.m4a')
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
            accept: "audio/mpeg,audio/wav,audio/ogg,audio/flac,audio/aac,audio/mp4",
            style: "display: none",
            onchange: async function() {
                if (fileInput.files.length) {
                    const file = fileInput.files[0];
                    await uploadAudio(file);
                    // Update the audio list in the node
                    const audioWidget = this.widgets.find(w => w.name === "audio");
                    if (audioWidget) {
                        // Refresh the widget's values
                        audioWidget.options.values = await getAudioList();
                        audioWidget.value = file.name;
                        if (audioWidget.callback) {
                            audioWidget.callback(file.name);
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
        } else if (nodeData.name === "FSLoadAudio") {
            // addAudioUploadFeature(nodeType, nodeData);
        }
    }
});