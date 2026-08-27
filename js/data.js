// Content-only data: anatomy descriptions, portal definitions, pathology notes.
// Kept separate from geometry/scene code so teaching text is easy to review or extend.

export const STRUCTURES = {
  bone: {
    name: 'Bone (Scapula, Humerus & Clavicle)',
    note: 'The glenohumeral joint is a ball-and-socket joint: the large humeral head articulates with the shallow glenoid fossa of the scapula. The acromion and coracoid process form the coracoacromial arch above the joint; the clavicle links the scapula to the axial skeleton via the AC joint.'
  },
  labrum: {
    name: 'Glenoid Labrum',
    note: 'A ring of fibrocartilage attached to the rim of the glenoid that deepens the socket by ~50% and provides a suction-seal effect, adding stability to an otherwise shallow joint.'
  },
  capsule: {
    name: 'Joint Capsule',
    note: 'A fibrous sleeve enclosing the joint, reinforced by the glenohumeral ligaments (superior, middle, inferior). It is the largest and loosest capsule in the body, allowing the shoulder its wide range of motion at the cost of stability.'
  },
  cuff_supraspinatus: {
    name: 'Supraspinatus Tendon',
    note: 'Runs from the supraspinatus fossa, under the acromion, to the greater tuberosity. Initiates abduction and is the most commonly torn rotator cuff tendon due to its position under the coracoacromial arch.'
  },
  cuff_infraspinatus: {
    name: 'Infraspinatus Tendon',
    note: 'Originates from the infraspinatus fossa on the posterior scapula and inserts on the greater tuberosity, posterior to supraspinatus. Primary external rotator of the humerus.'
  },
  cuff_teresMinor: {
    name: 'Teres Minor Tendon',
    note: 'A smaller external rotator, running just inferior to infraspinatus from the lateral scapular border to the greater tuberosity.'
  },
  cuff_subscapularis: {
    name: 'Subscapularis Tendon',
    note: 'The only rotator cuff tendon on the anterior scapula, inserting on the lesser tuberosity. The main internal rotator and an important anterior stabilizer.'
  },
  biceps: {
    name: 'Long Head of Biceps Tendon',
    note: 'Originates from the supraglenoid tubercle and superior labrum, passes intra-articularly over the humeral head, and exits the joint through the bicipital (intertubercular) groove. A common source of anterior shoulder pain and often assessed during arthroscopy.'
  }
};

// Portal geometry is expressed as simple [x,y,z] arrays consumed by anatomy.js / main.js.
// `position` = skin-entry / pivot point for the scope. `target` = initial aim point inside the joint.
export const PORTALS = {
  posterior: {
    name: 'Posterior Portal',
    role: 'Primary viewing portal',
    position: [0.6, 0.5, -2.3],
    target: [0.15, 0.05, -0.1],
    workingPortal: 'anterior',
    desc: 'The workhorse viewing portal, ~2cm inferior and medial to the posterolateral corner of the acromion ("soft spot"). Gives a broad view of the glenohumeral joint, labrum and rotator cuff undersurface.'
  },
  anterior: {
    name: 'Anterior (Mid-Glenoid) Portal',
    role: 'Viewing or working portal',
    position: [0.5, 0.15, 2.2],
    target: [0.0, 0.05, -0.3],
    workingPortal: 'lateral',
    desc: 'Established via an "outside-in" or "inside-out" technique lateral to the coracoid process. Used to inspect the anterior labrum, subscapularis and biceps origin, or as a working portal for anterior instrumentation.'
  },
  lateral: {
    name: 'Lateral (Subacromial) Portal',
    role: 'Viewing or working portal',
    position: [-0.3, 2.6, -0.35],
    target: [-0.15, 0.9, -0.25],
    workingPortal: 'posterior',
    desc: 'Placed lateral to the acromion, roughly in line with the posterior portal. Used to enter the subacromial space and assess the bursal-side rotator cuff and coracoacromial arch.'
  }
};

export const PATHOLOGIES = {
  normal: {
    label: 'Normal Anatomy',
    summary: 'Intact glenoid labrum, capsule and rotator cuff. This is the baseline appearance used to judge pathology against during diagnostic arthroscopy.'
  },
  bankart: {
    label: 'Bankart Lesion (Labral Tear)',
    summary: 'Detachment of the anteroinferior labrum (and often the anterior band of the inferior glenohumeral ligament) from the glenoid rim, classically caused by anterior shoulder dislocation. Arthroscopically it appears as a gap between the labrum and the glenoid, sometimes with a stripped, mobile labral fragment ("floating" labrum) that can be probed away from the bone.'
  },
  cuffTear: {
    label: 'Rotator Cuff Tear (Supraspinatus)',
    summary: 'A full-thickness tear of the supraspinatus tendon at its footprint on the greater tuberosity. The retracted tendon stump and an exposed, bare footprint of bone are characteristic arthroscopic findings, best seen from the lateral subacromial portal.'
  }
};

export const MODES = {
  external: 'external',
  arthroscopic: 'arthroscopic'
};
