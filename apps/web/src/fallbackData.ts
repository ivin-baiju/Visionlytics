// Auto-generated from real ONNX Runtime evaluation runs (apps/ml/visionlytics_ml/eval_harness.py)
export const DEFAULT_BENCHMARKS = {
  "evaluatedAt": "2026-11-04T18:00:16Z",
  "hardware": {
    "machine": "arm64",
    "processor": "arm",
    "python": "3.12.13",
    "onnxruntime": "1.31.1",
    "providers": [
      "CoreMLExecutionProvider",
      "AzureExecutionProvider",
      "CPUExecutionProvider"
    ]
  },
  "models": {
    "balanced": {
      "name": "RT-DETRv2-R18vd-INT8",
      "licence": "Apache-2.0",
      "sizeMb": 20.02,
      "latencyP50Ms": 169.06,
      "latencyP95Ms": 175.17,
      "fpsP50": 5.92
    },
    "fast": {
      "name": "YOLOS-Tiny-INT8 (416x416)",
      "licence": "Apache-2.0",
      "sizeMb": 6.46,
      "latencyP50Ms": 98.14,
      "latencyP95Ms": 100.74,
      "fpsP50": 10.19
    }
  },
  "metrics": {
    "mAP50": 0.9143,
    "mAP50_95": 0.8514,
    "personCountMAE": 0.0,
    "personExactMatchRate": 1.0,
    "colourNamingAccuracy": 0.8571,
    "trackIdSwitchesPerMin": 0.0,
    "trackIdentityPreservation": 1.0
  }
};

export const DEFAULT_SAMPLES = [
  {
    id: "bus_street",
    title: "Scene: Urban street",
    dataUrl: "/samples/bus_street.jpg",
  },
  {
    id: "zidane_people",
    title: "Scene: Close subjects",
    dataUrl: "/samples/zidane_people.jpg",
  },
];

export const PRECOMPUTED_ONNX_FRAMES: Record<string, any> = {
  bus_street: {
  "width": 810,
  "height": 1080,
  "preset": "balanced",
  "architecture": "rtdetr-v2-r18vd-int8",
  "latencyMs": 1095.51,
  "peopleCount": 4,
  "uncertainCount": 7,
  "detections": [
    {
      "trackId": 1,
      "label": "person",
      "confidence": 0.9311,
      "uncertain": false,
      "bbox": {
        "x1": 49.3,
        "y1": 399.0,
        "x2": 247.2,
        "y2": 905.0
      },
      "colours": [
        {
          "name": "Tan",
          "hex": "#b08c5e",
          "share": 0.53
        },
        {
          "name": "Off-White",
          "hex": "#ece8de",
          "share": 0.27
        },
        {
          "name": "Navy",
          "hex": "#1d2c4d",
          "share": 0.2
        }
      ],
      "upperClothingColours": [
        {
          "name": "Slate Grey",
          "hex": "#656d75",
          "share": 0.54
        },
        {
          "name": "Off-White",
          "hex": "#ece8de",
          "share": 0.46
        }
      ],
      "lowerClothingColours": [
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.55
        },
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.45
        }
      ],
      "trajectory": [
        {
          "frame": 0,
          "cx": 148.2,
          "cy": 652.0
        }
      ]
    },
    {
      "trackId": 2,
      "label": "person",
      "confidence": 0.9074,
      "uncertain": false,
      "bbox": {
        "x1": 668.9,
        "y1": 389.6,
        "x2": 810.0,
        "y2": 881.5
      },
      "colours": [
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.45
        },
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.4
        },
        {
          "name": "Cobalt Blue",
          "hex": "#1f549c",
          "share": 0.16
        }
      ],
      "upperClothingColours": [
        {
          "name": "Navy",
          "hex": "#1d2c4d",
          "share": 0.83
        },
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.17
        }
      ],
      "lowerClothingColours": [
        {
          "name": "Off-White",
          "hex": "#ece8de",
          "share": 0.82
        },
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.18
        }
      ],
      "trajectory": [
        {
          "frame": 0,
          "cx": 739.5,
          "cy": 635.5
        }
      ]
    },
    {
      "trackId": 3,
      "label": "bus",
      "confidence": 0.8946,
      "uncertain": false,
      "bbox": {
        "x1": 14.5,
        "y1": 230.9,
        "x2": 805.3,
        "y2": 737.8
      },
      "colours": [
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.47
        },
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.33
        },
        {
          "name": "Cobalt Blue",
          "hex": "#1f549c",
          "share": 0.2
        }
      ],
      "trajectory": [
        {
          "frame": 0,
          "cx": 409.9,
          "cy": 484.3
        }
      ]
    },
    {
      "trackId": 4,
      "label": "person",
      "confidence": 0.8934,
      "uncertain": false,
      "bbox": {
        "x1": 224.5,
        "y1": 405.8,
        "x2": 342.6,
        "y2": 859.8
      },
      "colours": [
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.5
        },
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.28
        },
        {
          "name": "Rust",
          "hex": "#9e4325",
          "share": 0.22
        }
      ],
      "upperClothingColours": [
        {
          "name": "Espresso Brown",
          "hex": "#4b3425",
          "share": 0.59
        },
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.41
        }
      ],
      "lowerClothingColours": [
        {
          "name": "Navy",
          "hex": "#1d2c4d",
          "share": 0.77
        },
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.23
        }
      ],
      "trajectory": [
        {
          "frame": 0,
          "cx": 283.6,
          "cy": 632.8
        }
      ]
    },
    {
      "trackId": 5,
      "label": "person",
      "confidence": 0.8411,
      "uncertain": false,
      "bbox": {
        "x1": 0.0,
        "y1": 556.8,
        "x2": 71.8,
        "y2": 870.0
      },
      "colours": [
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.4
        },
        {
          "name": "Espresso Brown",
          "hex": "#4b3425",
          "share": 0.38
        },
        {
          "name": "Cobalt Blue",
          "hex": "#1f549c",
          "share": 0.21
        }
      ],
      "upperClothingColours": [
        {
          "name": "Slate Grey",
          "hex": "#656d75",
          "share": 0.58
        },
        {
          "name": "Beige",
          "hex": "#d4c2a3",
          "share": 0.42
        }
      ],
      "lowerClothingColours": [
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.61
        },
        {
          "name": "Off-White",
          "hex": "#ece8de",
          "share": 0.39
        }
      ],
      "trajectory": [
        {
          "frame": 0,
          "cx": 35.9,
          "cy": 713.4
        }
      ]
    }
  ],
  "uniqueTrackCount": 5
},
  zidane_people: {
  "width": 1280,
  "height": 720,
  "preset": "balanced",
  "architecture": "rtdetr-v2-r18vd-int8",
  "latencyMs": 475.01,
  "peopleCount": 2,
  "uncertainCount": 4,
  "detections": [
    {
      "trackId": 1,
      "label": "person",
      "confidence": 0.9113,
      "uncertain": false,
      "bbox": {
        "x1": 744.9,
        "y1": 42.3,
        "x2": 1149.8,
        "y2": 712.8
      },
      "colours": [
        {
          "name": "Black",
          "hex": "#16181a",
          "share": 0.48
        },
        {
          "name": "Slate Grey",
          "hex": "#656d75",
          "share": 0.35
        },
        {
          "name": "Silver Grey",
          "hex": "#a6adb4",
          "share": 0.17
        }
      ],
      "upperClothingColours": [
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.7
        },
        {
          "name": "Silver Grey",
          "hex": "#a6adb4",
          "share": 0.3
        }
      ],
      "lowerClothingColours": [
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.77
        },
        {
          "name": "Silver Grey",
          "hex": "#a6adb4",
          "share": 0.23
        }
      ],
      "trajectory": [
        {
          "frame": 1,
          "cx": 947.3,
          "cy": 377.5
        }
      ]
    },
    {
      "trackId": 2,
      "label": "person",
      "confidence": 0.8981,
      "uncertain": false,
      "bbox": {
        "x1": 116.2,
        "y1": 199.7,
        "x2": 1135.6,
        "y2": 713.4
      },
      "colours": [
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.44
        },
        {
          "name": "Espresso Brown",
          "hex": "#4b3425",
          "share": 0.31
        },
        {
          "name": "Silver Grey",
          "hex": "#a6adb4",
          "share": 0.25
        }
      ],
      "upperClothingColours": [
        {
          "name": "Espresso Brown",
          "hex": "#4b3425",
          "share": 0.6
        },
        {
          "name": "Slate Grey",
          "hex": "#656d75",
          "share": 0.4
        }
      ],
      "lowerClothingColours": [
        {
          "name": "Slate Grey",
          "hex": "#656d75",
          "share": 0.54
        },
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.46
        }
      ],
      "trajectory": [
        {
          "frame": 1,
          "cx": 625.9,
          "cy": 456.5
        }
      ]
    },
    {
      "trackId": 3,
      "label": "tie",
      "confidence": 0.7353,
      "uncertain": false,
      "bbox": {
        "x1": 354.4,
        "y1": 433.5,
        "x2": 530.0,
        "y2": 717.5
      },
      "colours": [
        {
          "name": "Black",
          "hex": "#16181a",
          "share": 0.43
        },
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.41
        },
        {
          "name": "Silver Grey",
          "hex": "#a6adb4",
          "share": 0.16
        }
      ],
      "trajectory": [
        {
          "frame": 1,
          "cx": 442.2,
          "cy": 575.5
        }
      ]
    },
    {
      "trackId": 4,
      "label": "tie",
      "confidence": 0.5372,
      "uncertain": false,
      "bbox": {
        "x1": 989.6,
        "y1": 313.5,
        "x2": 1054.0,
        "y2": 414.8
      },
      "colours": [
        {
          "name": "Black",
          "hex": "#16181a",
          "share": 0.54
        },
        {
          "name": "Off-White",
          "hex": "#ece8de",
          "share": 0.24
        },
        {
          "name": "Charcoal",
          "hex": "#32363b",
          "share": 0.22
        }
      ],
      "trajectory": [
        {
          "frame": 1,
          "cx": 1021.8,
          "cy": 364.1
        }
      ]
    }
  ],
  "uniqueTrackCount": 4
},
};
