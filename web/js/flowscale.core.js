import { app } from '../../../scripts/app.js'

async function uploadVideo(file) {
    try {
        // Wrap file in formdata so it includes filename
        const body = new FormData();
        const new_file = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
        });
        body.append("video", new_file);
        
        const resp = await api.fetchApi("/upload/video", {
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
            async onchange() {
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
            }.bind(this),
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
        // Add upload support to FSLoadVideo node
        if (nodeData.name === "FSLoadVideo") {
            addVideoUploadFeature(nodeType, nodeData);
        }
    }
});