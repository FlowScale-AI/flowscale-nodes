import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// Load the Flowscale CSS
const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = 'extensions/flowscale-nodes/web/css/emoji.css';
document.head.appendChild(link);

// Override node title handling
function setupFlowscaleNode(node, nodeData) {
    const origGetTitle = node.constructor.prototype.getTitle;
    node.constructor.prototype.getTitle = function() {
        const title = origGetTitle.call(this);
        if (title && title.includes('flowscale-icon')) {
            const container = document.createElement('div');
            container.style.display = 'flex';
            container.style.alignItems = 'center';
            container.style.justifyContent = 'center';
            container.style.gap = '4px';
            
            const icon = document.createElement('span');
            icon.className = 'flowscale-icon';
            
            // Extract plain text title
            const temp = document.createElement('div');
            temp.innerHTML = title;
            const plainText = document.createTextNode(temp.textContent || temp.innerText);
            
            container.appendChild(icon);
            container.appendChild(plainText);
            return container;
        }
        return title;
    };
}

async function uploadVideo(file) {
    try {
        // Wrap file in formdata so it includes filename
        const body = new FormData();
        const new_file = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
        });
        body.append("image", new_file);
        
        const resp = await api.fetchApi("/upload/image", {
            method: "POST",
            body,
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
        const res = await api.fetchApi('/fs/get_video_files');  // Fixed endpoint URL
        if (res.status === 200) {
            const data = await res.json();
            return data.files || [];
        }
        return [];
    } catch (error) {
        console.error("Error fetching video files:", error);
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
        
        if (nodeData.name === "FSLoadVideo") {
            addVideoUploadFeature(nodeType, nodeData);
        }
    }
});