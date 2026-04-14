import { Router, type IRouter } from "express";
import healthRouter from "./health";
import activityRouter from "./activity";
import adminRouter from "./admin";
import agentsRouter from "./agents";
import intelligenceRouter from "./intelligence";
import mediaRouter from "./media";
import videoRouter from "./video";

const router: IRouter = Router();

router.use(healthRouter);
router.use(activityRouter);
router.use(adminRouter);
router.use(agentsRouter);
router.use(intelligenceRouter);
router.use(mediaRouter);
router.use(videoRouter);

export default router;
