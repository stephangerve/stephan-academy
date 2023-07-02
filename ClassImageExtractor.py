import keyboard
import random
import string
import cv2
import mss
import mss.tools
import screeninfo
import numpy as np
import Config
import time
import os
import io
from PIL import Image
import cv2



class ImageExtractor:

    def __init__(self, ui, extracted_image_arrays):
        self.ui = ui
        self.extracted_image_arrays = extracted_image_arrays
        self.x_cursor, self.y_cursor = 0, 0
        self.x_start, self.y_start, self.x_end, self.y_end = 0, 0, 0, 0
        self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = 0, 0, 0, 0
        self.sc_x_center, self.sc_y_center = 0, 0
        self.drawing_boundary = False
        self.drawing_bbox = False
        self.drawing_bboxes = False  # formerly drawing
        self.drawing_column_line = False
        self.drawing_subcolumns = False
        self.drawing_sc_rows = False
        self.drawing_bbox_outer_boundary = False
        self.drawing_grid_outer_boundary = False
        self.drawing_grid_column_bboxes = False
        self.drawing_one_gcb = False
        self.outer_boundary = [(0, 0), (0, 0)]
        self.column_line = [(0, 0), (0, 0)]
        self.header = []
        # self.one_column_boundary_set = False
        # self.two_columns_boundary_set = False
        self.label_ready = False
        self.mask_x_offset = 20
        self.mask_y_offset = 20
        self.mask_x_start, self.mask_y_start, self.mask_x_end, self.mask_y_end = None, None, None, None
        self.drawing_mask = False
        self.im_bnd_gray = None
        self.im_thresh_bin = None
        self.mask_offset_found = False
        self.white_columns = None
        self.automatic_bbox_detect_mode = False
        self.mask_reg_col_line = [(0, 0), (0, 0)]
        self.annotate_mode = None
        self.bboxes = {}
        self.grid_col_bboxes = []
        self.masks = {}
        self.screenshots = []
        self.index_number = None
        self.annotations = {}
        # Image arrays
        self.orig_image = None
        self.image_w_border = None
        self.image_w_outer_boundary = None
        self.image_w_mask = None
        self.image_w_bboxes = None
        self.scan_mode = None
        self.command = None
        self.unprocessed_reg_boundary = None
        self.column_position = None
        self.grid_outer_boundary = False
        self.boundary_left_column = None
        self.boundary_right_column = None
        self.mouse_clicked = None
        self.image_finalized = None

    def takeScreenshot(self):

        with mss.mss() as sct:
            monitor_number = Config.MONITOR_NUMBER
            mon = sct.monitors[monitor_number]
            monitor = {
                "top": mon["top"],
                "left": mon["left"],
                "width": mon["width"],
                "height": mon["height"],
                "mon": monitor_number,
            }
            self.sct_img = sct.grab(monitor)
        return np.array(self.sct_img)

    def annotateOneColumn(self, command, current_set, IMAGE_TYPE, ret_current_index_number):
        self.IMAGE_TYPE = IMAGE_TYPE
        self.index_number = ret_current_index_number() + self.ui.default_idx_inc_spinbox.value()
        if command not in Config.STANDARD_OPs:
            self.annotate_mode = Config.OP_SIMPLE
        elif command == Config.OP_APP_TO_LAST and len(self.extracted_image_arrays) == 0:
            self.annotate_mode = Config.OP_SIMPLE
        elif command == Config.OP_APP_TO_LAST and len(self.extracted_image_arrays) > 0:
            self.index_number = ret_current_index_number()
            self.annotate_mode = Config.OP_APP_TO_LAST
        elif command == Config.OP_COMBINE_W_H and len(self.header) == 0:
            self.annotate_mode = Config.OP_SIMPLE
        else:
            self.annotate_mode = command
        one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary = False, False, False
        self.orig_image = self.takeScreenshot()
        self.image_w_border = cv2.rectangle(self.orig_image.copy(), (0, 0), (self.orig_image.shape[1], self.orig_image.shape[0]), Config.NEON_GREEN, 4)

        cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty("image", cv2.WND_PROP_TOPMOST, 1)
        screen = screeninfo.get_monitors()[0]
        cv2.moveWindow("image", screen.x - 1, screen.y - 1)
        condition, one_column_boundary_set, two_columns_boundary_set = self.drawOuterBoundary(one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary)
        if condition:
            self.bboxes = {}
            self.masks = {}
            self.annotations = {}
            while True:
                self.column_position = None
                condition = self.drawBBoxes()
                if condition:
                    condition = self.delayToInspect()
                    if condition:
                        cv2.destroyAllWindows()
                        self.processImageWithBBoxes(current_set)
                        break
                else:
                    break
        cv2.destroyAllWindows()
        return

    def annotateTwoColumns(self, command, current_set, IMAGE_TYPE, ret_current_index_number):
        self.IMAGE_TYPE = IMAGE_TYPE
        self.index_number = ret_current_index_number() + self.ui.default_idx_inc_spinbox.value()
        if command not in Config.STANDARD_OPs:
            self.annotate_mode = Config.OP_SIMPLE
        elif command == Config.OP_APP_TO_LAST and len(self.extracted_image_arrays) == 0:
            self.annotate_mode = Config.OP_SIMPLE
        elif command == Config.OP_APP_TO_LAST and len(self.extracted_image_arrays) > 0:
            self.annotate_mode = Config.OP_APP_TO_LAST
        elif command == Config.OP_COMBINE_W_H and len(self.header) == 0:
            self.annotate_mode = Config.OP_SIMPLE
        else:
            self.annotate_mode = command
        one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary = False, False, False
        self.orig_image = self.takeScreenshot()
        self.image_w_border = cv2.rectangle(self.orig_image.copy(), (0, 0), (self.orig_image.shape[1], self.orig_image.shape[0]), Config.NEON_GREEN, 4)

        cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty("image", cv2.WND_PROP_TOPMOST, 1)
        screen = screeninfo.get_monitors()[0]
        cv2.moveWindow("image", screen.x - 1, screen.y - 1)

        condition, one_column_boundary_set, two_columns_boundary_set = self.drawOuterBoundary(one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary)
        if condition:
            condition, one_column_boundary_set, two_columns_boundary_set = self.drawColumnLine(one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary)
            if condition:
                self.annotations = {}
                self.bboxes = {}
                self.masks = {}
                while True:
                    self.outer_boundary = self.boundary_left_column
                    self.column_position = Config.COLUMN_LEFT
                    condition = self.drawBBoxes()
                    if condition:
                        self.outer_boundary = self.boundary_right_column
                        self.column_position = Config.COLUMN_RIGHT
                        condition = self.drawBBoxes()
                    else:
                        break
                    if condition:
                        condition = self.delayToInspect()
                        if condition:
                            cv2.destroyAllWindows()
                            self.processImageWithBBoxes(current_set)
                            break
                        else:
                            self.annotations = {}
                            self.bboxes = {}
                            self.masks = {}
        cv2.destroyAllWindows()
        return

    def drawBBoxes(self):
        grid_ordering = "horizontal"
        self.drawing_bboxes = True
        self.scan_mode = True
        if len(self.bboxes) > 0:
            if self.annotations[list(self.bboxes.keys())[-1]]["self.column_position"] != self.column_position and self.column_position in [Config.COLUMN_LEFT, Config.COLUMN_RIGHT]:
                code = self.generateCode()
                self.bboxes[code] = [(self.outer_boundary[0][0], self.outer_boundary[0][1]), (self.outer_boundary[1][0], self.outer_boundary[0][1])]
                self.addAnnotation(code=code, shape=Config.SHAPE_LINE, operation=None, column_pos=self.column_position, index=None)
        else:
            self.bboxes = {}
        self.image_w_outer_boundary_copy = self.image_w_outer_boundary.copy()
        if len(self.annotations) != 0:
            for key, bbox in zip(self.bboxes.keys(), self.bboxes.values()):
                if self.annotations[key]["shape"] != Config.SHAPE_LINE:
                    color = Config.BBOX_COLOR[self.annotations[key]["operation"]]
                    cv2.rectangle(self.image_w_outer_boundary_copy, bbox[0], bbox[1], color, 2)
                    if self.IMAGE_TYPE == "Exercises" and self.annotations[key]["operation"] in [Config.OP_SIMPLE, Config.OP_COMBINE_W_H]:
                        mask = self.masks[key]
                        if self.annotations[key]["grid"]:
                            mask_width = (mask[1][0] - mask[0][0])
                            im_region = self.image_w_outer_boundary_copy[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width]
                            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                            self.image_w_outer_boundary_copy[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width] = masked_reg
                            cv2.rectangle(self.image_w_outer_boundary_copy, (bbox[0][0], mask[0][1]), (bbox[0][0] + mask_width, mask[1][1]), color, 1)
                        else:
                            im_region = self.image_w_outer_boundary_copy[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]]
                            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                            self.image_w_outer_boundary_copy[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]] = masked_reg
                            cv2.rectangle(self.image_w_outer_boundary_copy, mask[0], mask[1], color, 1)
                    x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
                    label_x_start, label_y_start, label_x_end, label_y_end = x_0 - 28, y_0, x_1 - 2, y_1 + 20
                    cv2.rectangle(self.image_w_outer_boundary_copy, (label_x_start, label_y_start), (label_x_end, label_y_end), color, -1)
                    if self.annotations[key]["operation"] in [Config.OP_SET_HEADER, Config.OP_APP_TO_HEAD]:
                        label_str = "HEAD"
                        font_size = 0.30
                    else:
                        label_str = str(self.annotations[key]["index"]).zfill(3)
                        font_size = 0.40
                    cv2.putText(self.image_w_outer_boundary_copy, label_str, (label_x_start + 2, label_y_start + 14), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 1, cv2.LINE_AA)
        self.im_bnd_gray = cv2.cvtColor(self.orig_image, cv2.COLOR_BGR2GRAY)
        _, self.im_thresh_bin = cv2.threshold(self.im_bnd_gray, 240, 255, cv2.THRESH_BINARY)
        self.drawing_bbox_outer_boundary = True
        self.drawing_bbox = True
        self.image_finalized = self.image_w_outer_boundary_copy.copy()
        while self.drawing_bboxes:
            self.image_w_bboxes = self.image_finalized.copy()
            if self.annotate_mode in Config.BBOX_COLOR.keys():
                color = Config.BBOX_COLOR[self.annotate_mode]
            else:
                color = Config.RED
            if len(self.bboxes) > 0:
                self.unprocessed_reg_boundary = [(self.outer_boundary[0][0], list(self.bboxes.values())[-1][1][1]), self.outer_boundary[1]]
            else:
                self.unprocessed_reg_boundary = self.outer_boundary
            if self.annotate_mode in [Config.OP_SIMPLE, Config.OP_COMBINE_W_H]:
                cv2.setMouseCallback("image", self.SASOuterBoundaryAndMaskRegion)
                cv2.rectangle(self.image_w_bboxes, (self.x_start, self.y_start), (self.x_end, self.y_end), color, 1)
                cv2.line(self.image_w_bboxes, self.mask_reg_col_line[0], self.mask_reg_col_line[1], color, 1)
                if self.label_ready:
                    cv2.rectangle(self.image_w_bboxes, (self.label_x_start, self.label_y_start), (self.label_x_end, self.label_y_end), color, -1)
                    label_str = str(self.index_number).zfill(3)
                    font_size = 0.40
                    cv2.putText(self.image_w_bboxes, label_str, (self.label_x_start + 2, self.label_y_start + 14), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow("image", self.image_w_bboxes)
                cv2.waitKey(1)
                if self.drawing_bbox_outer_boundary is False and self.bboxArea([(self.x_start, self.y_start), (self.x_end, self.y_end)]) > 0:
                    self.index_number = self.setBBoxesAutomatically([(self.x_start, self.y_start), (self.x_end, self.y_end)], self.index_number, self.ui.default_idx_inc_spinbox.value(), False)
                    self.drawing_bbox_outer_boundary = True
                elif self.bboxArea([(self.x_start, self.y_start), (self.x_end, self.y_end)]) == 0:
                    self.drawing_bbox_outer_boundary = True
            elif self.annotate_mode in [Config.OP_APP_TO_LAST, Config.OP_SET_HEADER, Config.OP_APP_TO_HEAD]:
                cv2.setMouseCallback("image", self.scanAndSetBBOXCoordiates)
                if self.drawing_bbox is True:
                    cv2.rectangle(self.image_w_bboxes, (self.x_start, self.y_start), (self.x_end, self.y_end), color, 1)
                if self.label_ready:
                    cv2.rectangle(self.image_w_bboxes, (self.label_x_start, self.label_y_start), (self.label_x_end, self.label_y_end), color, -1)
                    if self.annotate_mode == Config.OP_SET_HEADER or self.annotate_mode == Config.OP_APP_TO_HEAD:
                        label_str = "HEAD"
                        font_size = 0.30
                    else:
                        label_str = str(self.index_number).zfill(3)
                        font_size = 0.40
                    cv2.putText(self.image_w_bboxes, label_str, (self.label_x_start + 2, self.label_y_start + 14), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 1, cv2.LINE_AA)
                    if self.IMAGE_TYPE == "Exercises" and self.annotate_mode in [Config.OP_SIMPLE, Config.OP_COMBINE_W_H]:
                        self.mask_x_start, self.mask_y_start, self.mask_x_end, self.mask_y_end = self.x_start, self.y_start, self.x_start + self.mask_x_offset, self.y_start + self.mask_y_offset
                        if self.mask_y_end >= self.y_end:
                            im_region = self.image_w_bboxes[self.mask_y_start:self.y_end, self.mask_x_start:self.mask_x_end]
                            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                            self.image_w_bboxes[self.mask_y_start:self.y_end, self.mask_x_start:self.mask_x_end] = masked_reg
                            cv2.rectangle(self.image_w_bboxes, (self.mask_x_start, self.mask_y_start), (self.mask_x_end, self.y_end), color, 1)
                        else:
                            im_region = self.image_w_bboxes[self.mask_y_start:self.mask_y_end, self.mask_x_start:self.mask_x_end]
                            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                            self.image_w_bboxes[self.mask_y_start:self.mask_y_end, self.mask_x_start:self.mask_x_end] = masked_reg
                            cv2.rectangle(self.image_w_bboxes, (self.mask_x_start, self.mask_y_start), (self.mask_x_end, self.mask_y_end), color, 1)
                cv2.imshow("image", self.image_w_bboxes)
                cv2.waitKey(1)

                if self.drawing_bbox is False and self.bboxArea([(self.x_start, self.y_start), (self.x_end, self.y_end)]) > 0:
                    if self.annotate_mode == Config.OP_APP_TO_LAST:
                        code = self.generateCode()
                        self.bboxes[code] = [(self.x_start, self.y_start), (self.x_end, self.y_end)]
                        self.addAnnotation(code=code, shape=Config.SHAPE_BBOX, operation=Config.OP_APP_TO_LAST, column_pos=self.column_position, index=self.index_number, append_to_last_saved_image=True)
                        self.index_number += self.ui.default_idx_inc_spinbox.value()
                    elif self.annotate_mode == Config.OP_SET_HEADER:
                        header_bbox = [(self.x_start, self.y_start), (self.x_end, self.y_end)]
                        self.header = []
                        self.header.append(self.orig_image[header_bbox[0][1]:header_bbox[1][1], header_bbox[0][0]:header_bbox[1][0]])
                        code = self.generateCode()
                        self.bboxes[code] = [(self.x_start, self.y_start), (self.x_end, self.y_end)]
                        self.addAnnotation(code=code, shape=Config.SHAPE_BBOX, operation=Config.OP_SET_HEADER, column_pos=self.column_position, index=None)
                    elif self.annotate_mode == Config.OP_APP_TO_HEAD:  # in the future you will have amend this to account for parts of the header taken on different pages
                        header_bbox = [(self.x_start, self.y_start), (self.x_end, self.y_end)]
                        self.header.append(self.orig_image[header_bbox[0][1]:header_bbox[1][1], header_bbox[0][0]:header_bbox[1][0]])
                        code = self.generateCode()
                        self.bboxes[code] = header_bbox
                        self.addAnnotation(code=code, shape=Config.SHAPE_BBOX, operation=Config.OP_APP_TO_HEAD, column_pos=self.column_position, index=None)
                    cv2.rectangle(self.image_w_bboxes, (self.x_start, self.y_start), (self.x_end, self.y_end), color, 2)
                    cv2.imshow("image", self.image_w_bboxes)
                    cv2.waitKey(1)
                    if self.annotate_mode == Config.OP_APP_TO_LAST:
                        self.annotate_mode = Config.OP_SIMPLE
                    elif self.annotate_mode == Config.OP_SET_HEADER:
                        self.annotate_mode = Config.OP_COMBINE_W_H
                    elif self.annotate_mode == Config.OP_APP_TO_HEAD:
                        self.annotate_mode = Config.OP_COMBINE_W_H
                    self.image_finalized = self.image_w_bboxes
                    self.drawing_bbox = True
                    self.label_ready = False
                    self.mask_offset_found = False
                elif self.bboxArea([(self.x_start, self.y_start), (self.x_end, self.y_end)]) == 0:
                    self.drawing_bbox = True
                    self.label_ready = False
                    self.mask_offset_found = False
            else:
                if self.annotate_mode == Config.OP_APP_TO_LAST:
                    self.annotate_mode = Config.OP_SIMPLE
                elif self.annotate_mode in [Config.OP_SET_HEADER, Config.OP_APP_TO_HEAD]:
                    self.annotate_mode = Config.OP_COMBINE_W_H
                elif self.annotate_mode == Config.OP_GRID_MODE:
                    if len(self.header) > 0:
                        self.annotate_mode = Config.OP_COMBINE_W_H
                    else:
                        self.annotate_mode = Config.OP_SIMPLE
                condition = self.drawGridBBoxes()
                if condition:
                    cv2.setMouseCallback("image", self.scanAndSetBBOXCoordiates)

            if keyboard.is_pressed(Config.OP_SIMPLE):
                time.sleep(0.01)
                if self.annotate_mode != Config.OP_SIMPLE:
                    if self.annotate_mode == Config.OP_APP_TO_LAST:
                        self.index_number += self.ui.default_idx_inc_spinbox.value()
                    self.annotate_mode = Config.OP_SIMPLE
            elif keyboard.is_pressed(Config.OP_APP_TO_LAST):
                time.sleep(0.01)
                if self.annotate_mode != Config.OP_APP_TO_LAST:
                    #if len(os.listdir(Config.TEMP_SS_PATH)) == 0 and len(self.bboxes) == 0:
                    if len(self.extracted_image_arrays) == 0 and len(self.bboxes) == 0:
                        self.annotate_mode = Config.OP_SIMPLE
                    else:
                        self.annotate_mode = Config.OP_APP_TO_LAST
                        self.index_number -= self.ui.default_idx_inc_spinbox.value()
            elif keyboard.is_pressed(Config.OP_SET_HEADER):
                time.sleep(0.01)
                if self.annotate_mode != Config.OP_SET_HEADER:
                    if self.annotate_mode == Config.OP_APP_TO_LAST:
                        self.index_number += self.ui.default_idx_inc_spinbox.value()
                    self.annotate_mode = Config.OP_SET_HEADER
            elif keyboard.is_pressed(Config.OP_COMBINE_W_H):
                time.sleep(0.01)
                if self.annotate_mode != Config.OP_COMBINE_W_H:
                    if self.annotate_mode == Config.OP_APP_TO_LAST:
                        self.index_number += self.ui.default_idx_inc_spinbox.value()
                    if len(self.header) == 0:
                        self.annotate_mode = Config.OP_SIMPLE
                    else:
                        self.annotate_mode = Config.OP_COMBINE_W_H
            elif keyboard.is_pressed(Config.OP_APP_TO_HEAD):
                time.sleep(0.01)
                if self.annotate_mode != Config.OP_APP_TO_HEAD:
                    if self.annotate_mode == Config.OP_APP_TO_LAST:
                        self.index_number += self.ui.default_idx_inc_spinbox.value()
                    if len(self.header) == 0:
                        self.annotate_mode = Config.OP_SIMPLE
                    else:
                        self.annotate_mode = Config.OP_APP_TO_HEAD
            elif keyboard.is_pressed(Config.OP_GRID_MODE):
                time.sleep(0.01)
                if self.annotate_mode != Config.OP_GRID_MODE:
                    if self.annotate_mode == Config.OP_APP_TO_LAST:
                        self.index_number += self.ui.default_idx_inc_spinbox.value()
                    self.annotate_mode = Config.OP_GRID_MODE
            elif keyboard.is_pressed('ctrl+shift+alt+8'):
                while keyboard.is_pressed('ctrl+shift+alt+8'):
                    continue
                code = self.generateCode()
                self.bboxes[code] = [(self.x_start, self.y_end), (self.x_end, self.y_end)]
                self.addAnnotation(code=code, shape=Config.SHAPE_LINE, operation=8, column_pos=self.column_position, index=None)
                cv2.imshow("image", self.image_w_bboxes)
                cv2.waitKey(1)
                self.x_start, self.y_start, self.x_end, self.y_end = 0, 0, 0, 0
                self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = 0, 0, 0, 0
            elif keyboard.is_pressed('ctrl+shift+alt+9'):
                while keyboard.is_pressed('ctrl+shift+alt+9'):
                    continue
                if len(self.bboxes) > 0:
                    minimum = 0
                    for key in reversed(self.annotations):
                        if self.annotations[key]["index"] is not None:
                            minimum = self.annotations[key]["index"]
                    if self.index_number - 1 > minimum:
                        self.index_number -= self.ui.default_idx_inc_spinbox.value()
            elif keyboard.is_pressed('ctrl+shift+alt+0'):
                while keyboard.is_pressed('ctrl+shift+alt+0'):
                    continue
                self.index_number += self.ui.default_idx_inc_spinbox.value()
            elif keyboard.is_pressed('ctrl+shift+alt+x'):
                while keyboard.is_pressed('ctrl+shift+alt+x'):
                    continue
                if self.scan_mode:
                    self.scan_mode = False
                    cv2.setMouseCallback("image", self.setBBOXCoordiates)
                else:
                    self.scan_mode = True
                    cv2.setMouseCallback("image", self.scanAndSetBBOXCoordiates)
            elif keyboard.is_pressed('esc') or self.annotate_mode is Config.OP_CANCEL:
                while keyboard.is_pressed('esc'):
                    continue
                if len(self.bboxes) == 0:
                    self.drawing_bboxes = False
                    print("Canceled.")
                    return False
                else:
                    self.undoBBoxDrawing()
        return True

    def getCurrentMouseCoord(self, event, x, y, flags, param):
        self.x_start, self.y_start, self.x_end, self.y_end = x, y, x, y

    def setBBoxesAutomatically(self, boundary, index_number, index_increment, grid):
        self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
        mask_scan_region = self.im_thresh_bin[self.y_start:self.y_end, self.x_start:self.mask_reg_col_line[0][0]]
        min_pix_value, num_pos_y1 = self.binSearchForBBOXBoundaries("black", mask_scan_region, [i for i in range(self.y_start, self.y_end)], scan_up=False)
        min_pix_value, num_pos_y2 = self.binSearchForBBOXBoundaries("white", mask_scan_region[(num_pos_y1 - self.y_start):], [i for i in range(num_pos_y1, self.y_end)], scan_up=False)
        top_bbox_y = boundary[0][1]
        while True:
            min_pix_value, next_num_pos_y1 = self.binSearchForBBOXBoundaries("black", mask_scan_region[(num_pos_y2 - self.y_start):], [i for i in range(num_pos_y2, self.y_end)], scan_up=False)
            if min_pix_value >= 240:
                break
            upper_scan_region = self.im_thresh_bin[num_pos_y2:next_num_pos_y1, self.x_start:self.x_end]
            cont_white_regs = self.binSearchContiguousWhiteRegions(upper_scan_region, [i for i in range(num_pos_y2, next_num_pos_y1)], {})
            midpoint_y = self.findMidpointOfLongestContWhiteReg(cont_white_regs)
            if midpoint_y is None:
                break
            key = self.generateCode()
            bbox = [(self.x_start, top_bbox_y), (self.x_end, midpoint_y)]
            self.bboxes[key] = bbox
            if self.annotate_mode == Config.OP_SIMPLE:
                self.addAnnotation(code=key, shape=Config.SHAPE_BBOX, operation=self.annotate_mode, column_pos=self.column_position, index=index_number, grid=grid)
            elif self.annotate_mode == Config.OP_COMBINE_W_H:
                self.addAnnotation(code=key, shape=Config.SHAPE_BBOX, operation=self.annotate_mode, column_pos=self.column_position, index=index_number, header=self.header, grid=grid)
            index_number += index_increment
            mask = [(self.x_start, top_bbox_y), (self.mask_reg_col_line[0][0], midpoint_y)]
            self.masks[key] = mask
            if self.IMAGE_TYPE == "Exercises":
                im_region = self.image_w_bboxes[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]]
                white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                self.image_w_bboxes[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]] = masked_reg
            color = Config.BBOX_COLOR[self.annotate_mode]
            cv2.rectangle(self.image_w_bboxes, mask[0], mask[1], color, 2)
            cv2.rectangle(self.image_w_bboxes, bbox[0], bbox[1], color, 2)
            x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
            l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
            cv2.rectangle(self.image_w_bboxes, (l_x_0, l_y_0), (l_x_1, l_y_1), color, -1)
            cv2.putText(self.image_w_bboxes, str(self.annotations[key]["index"]).zfill(3), (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow("image", self.image_w_bboxes)
            cv2.waitKey(1)
            top_bbox_y = midpoint_y
            min_pix_value, num_pos_y2 = self.binSearchForBBOXBoundaries("white", mask_scan_region[(next_num_pos_y1 - self.y_start):], [i for i in range(next_num_pos_y1, self.y_end)], scan_up=False)
        key = self.generateCode()
        bbox = [(self.x_start, top_bbox_y), (self.x_end, self.y_end)]
        self.bboxes[key] = bbox
        if self.annotate_mode == Config.OP_SIMPLE:
            self.addAnnotation(code=key, shape=Config.SHAPE_BBOX, operation=self.annotate_mode, column_pos=self.column_position, index=index_number, grid=grid)
        elif self.annotate_mode == Config.OP_COMBINE_W_H:
            self.addAnnotation(code=key, shape=Config.SHAPE_BBOX, operation=self.annotate_mode, column_pos=self.column_position, index=index_number, header=self.header, grid=grid)
        index_number += index_increment
        mask = [(self.x_start, top_bbox_y), (self.mask_reg_col_line[0][0], self.y_end)]
        self.masks[key] = mask
        if self.IMAGE_TYPE == "Exercises":
            im_region = self.image_w_bboxes[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]]
            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
            self.image_w_bboxes[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]] = masked_reg
        cv2.rectangle(self.image_w_bboxes, mask[0], mask[1], Config.BBOX_COLOR[self.annotate_mode], 2)
        cv2.rectangle(self.image_w_bboxes, bbox[0], bbox[1], Config.BBOX_COLOR[self.annotate_mode], 2)
        x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
        l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
        cv2.rectangle(self.image_w_bboxes, (l_x_0, l_y_0), (l_x_1, l_y_1), Config.BBOX_COLOR[self.annotate_mode], -1)
        cv2.putText(self.image_w_bboxes, str(self.annotations[key]["index"]).zfill(3), (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("image", self.image_w_bboxes)
        cv2.waitKey(1)
        self.label_ready = False
        self.drawing_bbox_outer_boundary = True
        self.image_finalized = self.image_w_bboxes
        return index_number

    def bboxArea(self, bbox):
        height = bbox[1][1] - bbox[0][1]
        width = bbox[1][0] - bbox[0][0]
        return height * width

    def drawGridBBoxes(self):
        # 0. Initialize
        grid_scan_mode = True
        self.grid_col_bboxes = []
        #grid_col_masks = []
        cv2.setMouseCallback("image", self.SASGridOuterBoundary)
        self.drawing_grid_outer_boundary = True
        image_w_gob = self.image_w_bboxes.copy()
        line_bbox = [(self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1]), (self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1])]
        if self.annotate_mode == Config.OP_GRID_MODE:
            self.annotate_mode = Config.OP_COMBINE_W_H
        x_0, y_0, x_1, y_1 = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1]
        l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20

        # 1. Set outer boundary
        while self.drawing_grid_outer_boundary:
            image_w_gob = self.image_w_bboxes.copy()
            cv2.rectangle(image_w_gob, (l_x_0, l_y_0), (l_x_1, l_y_1), Config.GREEN, -1)
            cv2.putText(image_w_gob, "GRID", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, Config.WHITE, 1, cv2.LINE_AA)
            cv2.rectangle(image_w_gob, line_bbox[0], (self.x_end, self.y_end), Config.GREEN, 1)
            cv2.imshow("image", image_w_gob)
            cv2.waitKey(1)
            for command in Config.STANDARD_OPs + [Config.OP_CANCEL]:
                if keyboard.is_pressed(command):
                    while keyboard.is_pressed(command):
                        continue
                    self.drawing_grid_outer_boundary = False
                    self.annotate_mode = command
                    return False

        self.grid_outer_boundary = [line_bbox[0], (self.x_end, self.y_end)]
        cv2.rectangle(image_w_gob, (l_x_0, l_y_0), (l_x_1, l_y_1), Config.GREEN, -1)
        cv2.putText(image_w_gob, "GRID", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, Config.WHITE, 1, cv2.LINE_AA)
        cv2.rectangle(image_w_gob, self.grid_outer_boundary[0], self.grid_outer_boundary[1], Config.GREEN, 2)
        cv2.imshow("image", image_w_gob)
        cv2.waitKey(1)

        # 2. Set column bounding boxes along with masks
        cv2.setMouseCallback("image", self.SASGridColumnBBoxes)
        image_w_gcb = image_w_gob.copy()
        if self.annotate_mode in [Config.OP_SIMPLE, Config.OP_COMBINE_W_H]:
            color = Config.BBOX_COLOR[self.annotate_mode]
        else:
            color = Config.RED
        self.drawing_grid_column_bboxes = True
        self.drawing_one_gcb = True
        mask_reg_col_lines = []
        while self.drawing_grid_column_bboxes:
            image_w_gcb = image_w_gob.copy()
            if self.drawing_one_gcb:
                cv2.rectangle(image_w_gcb, (self.x_start, self.y_start), (self.x_end, self.y_end), color, 1)
                self.mask_x_start, self.mask_x_end = self.x_start, self.x_start + self.mask_x_offset
                if self.IMAGE_TYPE == "Exercises":
                    im_region = image_w_gcb[self.y_start:self.y_end, self.mask_x_start:self.mask_x_end]
                    white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                    masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                    image_w_gcb[self.y_start:self.y_end, self.mask_x_start:self.mask_x_end] = masked_reg
                cv2.rectangle(image_w_gcb, (self.mask_x_start, self.y_start), (self.mask_x_end, self.y_end), color, 1)
                cv2.imshow("image", image_w_gcb)
                cv2.waitKey(1)
            else:
                self.grid_col_bboxes.append([(self.x_start, self.y_start), (self.x_end, self.y_end)])
                cv2.rectangle(image_w_gcb, (self.x_start, self.y_start), (self.x_end, self.y_end), color, 2)
                self.mask_x_start, self.mask_x_end = self.x_start, self.x_start + self.mask_x_offset
                if self.IMAGE_TYPE == "Exercises":
                    #grid_col_masks.append([mask_x_start, mask_x_end])
                    im_region = image_w_gcb[self.y_start:self.y_end, self.mask_x_start:self.mask_x_end]
                    white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                    masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                    image_w_gcb[self.y_start:self.y_end, self.mask_x_start:self.mask_x_end] = masked_reg
                mask_reg_col_lines.append([(self.mask_x_end, self.grid_outer_boundary[0][1]), (self.mask_x_end, self.grid_outer_boundary[1][1])])
                cv2.rectangle(image_w_gcb, (self.mask_x_start, self.y_start), (self.mask_x_end, self.y_end), color, 1)
                cv2.imshow("image", image_w_gcb)
                cv2.waitKey(1)
                image_w_gob = image_w_gcb
                self.drawing_one_gcb = True
            if keyboard.is_pressed('ctrl+shift+alt+x'):
                while keyboard.is_pressed('ctrl+shift+alt+x'):
                    continue
                if grid_scan_mode:
                    grid_scan_mode = False
                else:
                    grid_scan_mode = True
            if keyboard.is_pressed('esc'):
                time.sleep(0.5)
                self.white_columns = None
                self.drawing_grid_column_bboxes = False
                self.drawing_one_gcb = False
                self.grid_col_bboxes = []
                print("Canceled.")
                return False
            elif keyboard.is_pressed('ctrl+shift+alt+1'):
                while keyboard.is_pressed('ctrl+shift+alt+1'):
                    continue
                self.annotate_mode = Config.OP_SIMPLE
                color = Config.BBOX_COLOR[self.annotate_mode]
            elif keyboard.is_pressed('ctrl+shift+alt+4'):
                while keyboard.is_pressed('ctrl+shift+alt+4'):
                    continue
                self.annotate_mode = Config.OP_COMBINE_W_H
                color = Config.BBOX_COLOR[self.annotate_mode]

        self.white_columns = None
        if [(self.x_start, self.y_start), (self.x_end, self.y_end)] not in self.grid_col_bboxes:
            # if IMAGE_TYPE == "Exercises":
            #     grid_col_masks.append([self.mask_x_start, self.mask_x_end])
            mask_reg_col_lines.append([(self.mask_x_end, self.grid_outer_boundary[0][1]), (self.mask_x_end, self.grid_outer_boundary[1][1])])
            self.grid_col_bboxes.append([(self.x_start, self.y_start), (self.x_end, self.y_end)])
            cv2.rectangle(image_w_gcb, (self.x_start, self.y_start), (self.x_end, self.y_end), color, 2)
            cv2.imshow("image", image_w_gcb)
            cv2.waitKey(1)

        # 3. Set row dividing lines
        idx_increment = len(self.grid_col_bboxes) + self.ui.default_idx_inc_spinbox.value()
        last_grid_index_numbers = []
        for grid_col_bbox, mask_reg_col_line, i in zip(self.grid_col_bboxes, mask_reg_col_lines, [i for i in range(len(self.grid_col_bboxes))]):
            self.mask_reg_col_line = mask_reg_col_line
            last_grid_index_number = self.setBBoxesAutomatically(grid_col_bbox, self.index_number + i * self.ui.default_idx_inc_spinbox.value(), idx_increment, True)
            last_grid_index_numbers.append(last_grid_index_number)
        #self.index_number = max(last_grid_index_numbers) - idx_increment + 1  # reason? look on pg 584 in stewart's calculus 9th trans. ed.
        self.index_number = max([annot_dict["index"] for annot_dict in self.annotations.values() if annot_dict["index"] is not None]) + self.ui.default_idx_inc_spinbox.value()

        # 4. ...
        key_lb_2 = self.generateCode()
        self.bboxes[key_lb_2] = [(self.unprocessed_reg_boundary[0][0], self.grid_outer_boundary[1][1]), (self.unprocessed_reg_boundary[1][0], self.grid_outer_boundary[1][1])]
        self.addAnnotation(code=key_lb_2, shape=Config.SHAPE_LINE, operation=self.annotate_mode, column_pos=self.column_position, index=None)

        if self.grid_outer_boundary[1][1] >= self.unprocessed_reg_boundary[1][1]:
            self.drawing_bboxes = False
        self.label_ready = False
        return True

    def drawOuterBoundary(self, one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary):
        self.drawing_bboxes = False
        if not two_columns_boundary_set:
            self.outer_boundary = [(0, 0), (0, 0)]
            self.column_line = [(0, 0), (0, 0)]
        if not one_column_boundary_set:
            self.outer_boundary = [(0, 0), (0, 0)]
        if one_column_boundary_set or two_columns_boundary_set:
            self.outer_boundary = setted_outer_boundary
            self.image_w_outer_boundary = cv2.rectangle(self.image_w_border.copy(), self.outer_boundary[0], self.outer_boundary[1], Config.NEON_GREEN, 2)
            cv2.imshow("image", self.image_w_outer_boundary)
            cv2.waitKey(1)
            self.drawing_bboxes = True
        else:
            cv2.setMouseCallback("image", self.setOuterBoundaryCoordiates, [])
            self.image_w_mask = self.image_w_border.copy()
            im_region = self.image_w_mask[0:self.image_w_border.shape[0], 0:self.image_w_border.shape[1]]
            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 40
            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
            self.image_w_mask[0:self.image_w_border.shape[0], 0:self.image_w_border.shape[1]] = masked_reg
            while True:
                if self.annotate_mode in Config.BBOX_COLOR.keys():
                    color = Config.BBOX_COLOR[self.annotate_mode]
                elif self.annotate_mode == Config.OP_GRID_MODE:
                    color = Config.GREEN
                else:
                    color = Config.RED
                self.image_w_outer_boundary = self.image_w_mask.copy()
                cv2.line(self.image_w_outer_boundary, (self.x_cursor, 0), (self.x_cursor, self.image_w_border.shape[0]), color, 1)
                cv2.line(self.image_w_outer_boundary, (0, self.y_cursor), (self.image_w_border.shape[1], self.y_cursor), color, 1)
                if self.drawing_boundary is True:
                    image_wo_mask = self.image_w_border.copy()
                    unmasked_reg = image_wo_mask[self.y_start:self.y_end, self.x_start:self.x_end]
                    self.image_w_outer_boundary[self.y_start:self.y_end, self.x_start:self.x_end] = unmasked_reg
                    cv2.rectangle(self.image_w_outer_boundary, (self.x_start, self.y_start), (self.x_end, self.y_end), Config.NEON_GREEN, 1)
                cv2.imshow("image", self.image_w_outer_boundary)
                cv2.waitKey(1)

                if self.drawing_boundary is False and self.drawing_bboxes is True:
                    break
                if keyboard.is_pressed(Config.STANDARD_OPs[0]):
                    time.sleep(0.01)
                    if self.annotate_mode != Config.OP_SIMPLE:
                        self.annotate_mode = Config.OP_SIMPLE
                elif keyboard.is_pressed(Config.STANDARD_OPs[1]):
                    time.sleep(0.01)
                    if self.annotate_mode != Config.OP_APP_TO_LAST:
                        #if len(os.listdir(Config.TEMP_SS_PATH)) == 0 and len(self.bboxes) == 0:
                        if len(self.extracted_image_arrays) == 0 and len(self.bboxes) == 0:
                            self.annotate_mode = Config.OP_SIMPLE
                        else:
                            self.annotate_mode = Config.OP_APP_TO_LAST
                elif keyboard.is_pressed(Config.STANDARD_OPs[2]):
                    time.sleep(0.01)
                    if self.annotate_mode != Config.OP_SET_HEADER:
                        self.annotate_mode = Config.OP_SET_HEADER
                elif keyboard.is_pressed(Config.STANDARD_OPs[3]):
                    time.sleep(0.01)
                    if self.annotate_mode != Config.OP_COMBINE_W_H:
                        if len(self.header) == 0:
                            self.annotate_mode = Config.OP_SIMPLE
                        else:
                            self.annotate_mode = Config.OP_COMBINE_W_H
                elif keyboard.is_pressed(Config.STANDARD_OPs[4]):
                    time.sleep(0.01)
                    if self.annotate_mode != Config.OP_APP_TO_HEAD:
                        if len(self.header) == 0:
                            self.annotate_mode = Config.OP_SIMPLE
                        else:
                            self.annotate_mode = Config.OP_APP_TO_HEAD
                elif keyboard.is_pressed(Config.STANDARD_OPs[5]):
                    time.sleep(0.01)
                    if self.annotate_mode != Config.OP_GRID_MODE:
                        self.annotate_mode = Config.OP_GRID_MODE
                if keyboard.is_pressed('esc'):
                    time.sleep(0.01)
                    self.drawing_bboxes = False
                    self.drawing_boundary = False
                    self.outer_boundary = [(0, 0), (0, 0)]
                    # self.one_column_boundary_set = False
                    self.column_line = [(0, 0), (0, 0)]
                    # self.two_columns_boundary_set = False
                    print("Canceled.")
                    return False, None, None
            self.image_w_outer_boundary = self.image_w_mask.copy()
            image_wo_mask = self.image_w_border.copy()
            unmasked_reg = image_wo_mask[self.y_start:self.y_end, self.x_start:self.x_end]
            self.image_w_outer_boundary[self.y_start:self.y_end, self.x_start:self.x_end] = unmasked_reg
            cv2.rectangle(self.image_w_outer_boundary, (self.x_start, self.y_start), (self.x_end, self.y_end), Config.NEON_GREEN, 2)
            cv2.imshow("image", self.image_w_outer_boundary)
            cv2.waitKey(1)
        self.x_start, self.y_start, self.x_end, self.y_end = 0, 0, 0, 0
        self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = 0, 0, 0, 0
        self.drawing_boundary = False
        return True, one_column_boundary_set, two_columns_boundary_set

    def drawColumnLine(self, one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary):
        if two_columns_boundary_set:
            image_w_column_line = cv2.line(self.image_w_outer_boundary, self.column_line[0], self.column_line[1], Config.NEON_GREEN, 2)
            cv2.imshow("image", image_w_column_line)
            cv2.waitKey(1)
            self.boundary_left_column = [(self.outer_boundary[0][0], self.outer_boundary[0][1]), (self.column_line[1][0], self.outer_boundary[1][1])]
            self.boundary_right_column = [(self.column_line[0][0], self.outer_boundary[0][1]), (self.outer_boundary[1][0], self.outer_boundary[1][1])]
        else:
            self.drawing_column_line = True
            # cv2.setMouseCallback("image", setColumnLineCoordiates, [boundary])
            im_bnd_gray = cv2.cvtColor(self.orig_image, cv2.COLOR_BGR2GRAY)
            _, self.im_thresh_bin = cv2.threshold(im_bnd_gray, 240, 255, cv2.THRESH_BINARY)
            cv2.setMouseCallback("image", self.scanAndSetColumnLineCoordiates)
            while True:
                image_w_column_line = self.image_w_outer_boundary.copy()
                if self.drawing_column_line is True:
                    cv2.line(image_w_column_line, (self.x_start, self.y_start), (self.x_end, self.y_end), Config.NEON_GREEN, 1)
                cv2.imshow("image", image_w_column_line)
                cv2.waitKey(1)

                if self.drawing_column_line is False:
                    self.boundary_left_column = [(self.outer_boundary[0][0], self.outer_boundary[0][1]), (self.x_end, self.outer_boundary[1][1])]
                    self.boundary_right_column = [(self.x_end, self.outer_boundary[0][1]), (self.outer_boundary[1][0], self.outer_boundary[1][1])]
                    break

                if keyboard.is_pressed('esc'):
                    time.sleep(0.01)
                    self.drawing_bboxes = False
                    self.outer_boundary = [(0, 0), (0, 0)]
                    # one_column_boundary_set = False
                    self.column_line = [(0, 0), (0, 0)]
                    # two_columns_boundary_set = False
                    print("Canceled.")
                    return False, None, None
            cv2.line(self.image_w_outer_boundary, (self.x_start, self.y_start), (self.x_end, self.y_end), Config.NEON_GREEN, 2)
            cv2.imshow("image", self.image_w_outer_boundary)
            cv2.waitKey(1)
        return True, one_column_boundary_set, two_columns_boundary_set

    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    def SASOuterBoundaryAndMaskRegion(self, event, x, y, flags, param):
        if self.drawing_bbox_outer_boundary and self.drawing_bboxes:
            scan_radius = self.ui.bbox_scan_radius_spinbox.value()
            if len(self.bboxes) == 0:
                if y > self.unprocessed_reg_boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                elif y < self.unprocessed_reg_boundary[0][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                else:
                    scan_region = self.im_thresh_bin[y - scan_radius:y + scan_radius, self.unprocessed_reg_boundary[0][0]:self.unprocessed_reg_boundary[1][0]]
                    offset = -scan_radius
                    reg_rows = {}
                    cont_rows = []
                    start = True
                    for i in range(len(scan_region)):
                        avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                        reg_rows[y + offset] = avg_pixel_val
                        offset += 1
                        if avg_pixel_val >= self.ui.scan_row_avg_color_threshold_spinbox.value():
                            if start is False:
                                row = [y + offset]
                                cont_rows.append(row)
                                start = True
                            else:
                                if len(cont_rows) > 0:
                                    cont_rows[-1].append(y + offset)
                        else:
                            start = False
                    idx = None
                    max_len = 0
                    for i in range(len(cont_rows)):
                        reg = cont_rows[i]
                        if (reg[-1] - reg[0]) > max_len:
                            max_len = reg[-1] - reg[0]
                            idx = i
                    if idx is not None:
                        if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                            midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                        else:
                            midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                        if midpoint > self.unprocessed_reg_boundary[1][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                        elif y < self.unprocessed_reg_boundary[0][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                        else:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], midpoint
                    # else:
                    #     self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], y

            else:
                # bb_x_start, bb_y_start, bb_x_end, bb_y_end = list(self.bboxes.values())[-1][0][0], list(self.bboxes.values())[-1][1][1], list(self.bboxes.values())[-1][1][0], \
                #                                              list(self.bboxes.values())[-1][1][1]
                #bb_x_start, bb_y_start, bb_x_end, bb_y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                #cv2.rectangle(self.image_w_bboxes, (bb_x_start, bb_y_start), (bb_x_end, bb_y_end), Config.BLACK, 1)
                #cv2.line(self.image_w_bboxes, self.mask_reg_col_line[0], self.mask_reg_col_line[1], Config.BLACK, 1)
                #cv2.imshow("image", self.image_w_bboxes)
                #cv2.waitKey(1)
                if y > self.unprocessed_reg_boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                elif y < self.unprocessed_reg_boundary[0][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                else:
                    # self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_end, bb_x_end, y
                    scan_region = self.im_thresh_bin[y - scan_radius:y + scan_radius, self.unprocessed_reg_boundary[0][0]:self.unprocessed_reg_boundary[1][0]]
                    offset = -scan_radius
                    cont_rows = []
                    start = True
                    for i in range(len(scan_region)):
                        avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                        # reg_rows[y + offset] = avg_pixel_val
                        offset += 1
                        if avg_pixel_val >= self.ui.scan_row_avg_color_threshold_spinbox.value():
                            if start is False:
                                row = [y + offset]
                                cont_rows.append(row)
                                start = True
                            else:
                                if len(cont_rows) > 0:
                                    cont_rows[-1].append(y + offset)
                        else:
                            start = False
                    idx = None
                    max_len = 0
                    for i in range(len(cont_rows)):
                        reg = cont_rows[i]
                        if (reg[-1] - reg[0]) > max_len:
                            max_len = reg[-1] - reg[0]
                            idx = i
                    if idx is not None:
                        if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                            midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                        else:
                            midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                        if midpoint > self.unprocessed_reg_boundary[1][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                        elif y < self.unprocessed_reg_boundary[0][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                        else:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], midpoint
                    # else:
                    #     self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, y

            if x < self.unprocessed_reg_boundary[0][0]:
                self.mask_reg_col_line = [(self.unprocessed_reg_boundary[0][0], self.y_start), (self.unprocessed_reg_boundary[0][0], self.y_end)]
            elif x > self.unprocessed_reg_boundary[1][0]:
                self.mask_reg_col_line = [(self.unprocessed_reg_boundary[1][0], self.y_start), (self.unprocessed_reg_boundary[1][0], self.y_end)]
            else:
                self.mask_reg_col_line = [(x, self.y_start), (x, self.y_end)]
                scan_radius = self.ui.mask_scan_radius_spinbox.value()
                scan_region = self.im_thresh_bin[self.unprocessed_reg_boundary[0][1]:self.unprocessed_reg_boundary[1][1], x - scan_radius:x + scan_radius]
                scan_region = np.transpose(scan_region)
                offset = -scan_radius
                reg_columns = {}
                cont_columns = []
                start = True
                for i in range(len(scan_region)):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    reg_columns[x + offset] = avg_pixel_val
                    offset += 1
                    if avg_pixel_val > 250:
                        if start is False:
                            column = [x + offset]
                            cont_columns.append(column)
                            start = True
                        else:
                            if len(cont_columns) > 0:
                                cont_columns[-1].append(x + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_columns)):
                    reg = cont_columns[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    if (cont_columns[idx][-1] - cont_columns[idx][0]) % 2 == 1:
                        midpoint = int((cont_columns[idx][-1] + cont_columns[idx][0]) / 2)
                    else:
                        midpoint = int(np.ceil((cont_columns[idx][-1] + cont_columns[idx][0]) / 2))
                    if midpoint > self.unprocessed_reg_boundary[1][0]:
                        self.mask_reg_col_line = [(self.unprocessed_reg_boundary[1][0], self.y_start), (self.unprocessed_reg_boundary[1][0], self.y_end)]
                    elif midpoint < self.unprocessed_reg_boundary[0][0]:
                        self.mask_reg_col_line = [(self.unprocessed_reg_boundary[0][0], self.y_start), (self.unprocessed_reg_boundary[0][0], self.y_end)]
                    else:
                        self.mask_reg_col_line = [(midpoint, self.y_start), (midpoint, self.y_end)]
                else:
                    # mask_reg_col_line = [(x, y_start), (x, y_end)]
                    pass

        self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = self.x_start - 28, self.y_start, self.x_start - 2, self.y_start + 20
        self.label_ready = True

        if event == cv2.EVENT_LBUTTONUP:
            self.drawing_bbox_outer_boundary = False
            if self.y_end >= self.unprocessed_reg_boundary[1][1]:
                self.drawing_bboxes = False

    # T(n) = 2T(n/2) + f(m) for n rows, m entries per row, so T(n) = Theta(nlgn)
    def binSearchForBBOXBoundaries(self, intensity_type, rows, rows_indices, scan_up):
        if len(rows) > 1:
            top_min_pixel_val, top_mpv_row_index = self.binSearchForBBOXBoundaries(intensity_type, rows[:int(np.ceil(len(rows) / 2))], rows_indices[:int(np.ceil(len(rows) / 2))], scan_up)
            bott_min_pixel_val, bott_mpv_row_index = self.binSearchForBBOXBoundaries(intensity_type, rows[int(np.ceil(len(rows) / 2)):], rows_indices[int(np.ceil(len(rows) / 2)):], scan_up)
            if intensity_type == "black":
                if top_min_pixel_val < bott_min_pixel_val:
                    return top_min_pixel_val, top_mpv_row_index
                elif bott_min_pixel_val < top_min_pixel_val:
                    return bott_min_pixel_val, bott_mpv_row_index
                elif top_min_pixel_val == bott_min_pixel_val:
                    if scan_up:
                        return top_min_pixel_val, max(top_mpv_row_index, bott_mpv_row_index)
                    else:
                        return top_min_pixel_val, min(top_mpv_row_index, bott_mpv_row_index)
            elif intensity_type == "white":
                if top_min_pixel_val > bott_min_pixel_val:
                    return top_min_pixel_val, top_mpv_row_index
                elif bott_min_pixel_val > top_min_pixel_val:
                    return bott_min_pixel_val, bott_mpv_row_index
                elif top_min_pixel_val == bott_min_pixel_val:
                    if scan_up:
                        return top_min_pixel_val, max(top_mpv_row_index, bott_mpv_row_index)
                    else:
                        return top_min_pixel_val, min(top_mpv_row_index, bott_mpv_row_index)

        else:
            return int(min(rows[0])), rows_indices[0]

    def binSearchContiguousWhiteRegions(self, rows, rows_indices, pixel_label_dict):
        if len(rows) > 1:
            pixel_label_dict = self.binSearchContiguousWhiteRegions(rows[:int(np.ceil(len(rows) / 2))], rows_indices[:int(np.ceil(len(rows) / 2))], pixel_label_dict)
            pixel_label_dict = self.binSearchContiguousWhiteRegions(rows[int(np.ceil(len(rows) / 2)):], rows_indices[int(np.ceil(len(rows) / 2)):], pixel_label_dict)
            return pixel_label_dict
        else:
            if self.ui.avg_intensity_bin_search_checkbox.isChecked():
                row_intensity = int(np.mean(rows[0]))
            else:
                row_intensity = int(min(rows[0]))
            if row_intensity > self.ui.bin_search_white_threshold_spinbox.value():
                pixel_label_dict[rows_indices[0]] = 1
                return pixel_label_dict
            else:
                pixel_label_dict[rows_indices[0]] = -1
                return pixel_label_dict

    def findMidpointOfLongestContWhiteReg(self, cont_white_regs):
        row_intensity_labels = list(cont_white_regs.values())
        row_indices = list(cont_white_regs.keys())
        max_length = 0
        max_cont_rows = []
        cont_rows = []
        length = 0
        start = False
        for row_intensity_label, row_index in zip(row_intensity_labels, row_indices):
            if row_intensity_label == 1:
                if start is False:
                    start = True
                cont_rows.append(row_index)
                length += 1
            else:
                if start is True:
                    if not self.ui.use_white_last_region_checkbox.isChecked():
                        if length >= max_length - int(max_length / 2):
                            max_cont_rows = cont_rows
                            max_length = length
                    else:
                        max_cont_rows = cont_rows
                    length = 0
                    cont_rows = []

                start = False
        if row_intensity_labels[-1] != -1:
            if not self.ui.use_white_last_region_checkbox.isChecked():
                if length >= max_length - int(max_length / 2):
                    max_cont_rows = cont_rows
            else:
                max_cont_rows = cont_rows
        if len(max_cont_rows) > 1:
            midpoint_y = int((max_cont_rows[-1] + max_cont_rows[1]) / 2)
            return midpoint_y
        elif len(max_cont_rows) == 1:
            return max_cont_rows[-1]
        else:
            return None

    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    ####################################################################################################################################################################################################
    def setColumnLineCoordiates(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            if x > self.outer_boundary[1][0]:
                self.x_start, self.y_start, self.x_end, self.y_end = self.outer_boundary[1][0], self.outer_boundary[0][1], self.outer_boundary[1][0], self.outer_boundary[1][1]
            elif x < self.outer_boundary[0][0]:
                self.x_start, self.y_start, self.x_end, self.y_end = self.outer_boundary[0][0], self.outer_boundary[0][1], self.outer_boundary[0][0], self.outer_boundary[1][1]
            else:
                self.x_start, self.y_start, self.x_end, self.y_end = x, self.outer_boundary[0][1], x, self.outer_boundary[1][1]
        if event == cv2.EVENT_LBUTTONUP:
            self.column_line = [(self.x_start, self.y_start), (self.x_end, self.y_end)]
            self.drawing_column_line = False

    def scanAndSetColumnLineCoordiates(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            if x > self.outer_boundary[1][0]:
                self.x_start, self.y_start, self.x_end, self.y_end = self.outer_boundary[1][0], self.outer_boundary[0][1], self.outer_boundary[1][0], self.outer_boundary[1][1]
            elif x < self.outer_boundary[0][0]:
                self.x_start, self.y_start, self.x_end, self.y_end = self.outer_boundary[0][0], self.outer_boundary[0][1], self.outer_boundary[0][0], self.outer_boundary[1][1]
            else:
                # self.x_start, self.y_start, self.x_end, self.y_end = x, outer_boundary[0][1], x, outer_boundary[1][1]
                scan_radius = self.ui.column_line_scan_radius_spinbox.value()
                scan_region = self.im_thresh_bin[self.outer_boundary[0][1]:self.outer_boundary[1][1], x - scan_radius:x + scan_radius]
                scan_region = np.transpose(scan_region)
                offset = -scan_radius
                reg_columns = {}
                cont_columns = []
                start = True
                for i in range(len(scan_region)):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    reg_columns[x + offset] = avg_pixel_val
                    offset += 1
                    if avg_pixel_val == 255:
                        if start is False:
                            column = [x + offset]
                            cont_columns.append(column)
                            start = True
                        else:
                            if len(cont_columns) > 0:
                                cont_columns[-1].append(x + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_columns)):
                    reg = cont_columns[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    if (cont_columns[idx][-1] - cont_columns[idx][0]) % 2 == 1:
                        midpoint = int((cont_columns[idx][-1] + cont_columns[idx][0]) / 2)
                    else:
                        midpoint = int(np.ceil((cont_columns[idx][-1] + cont_columns[idx][0]) / 2))
                    if midpoint > self.outer_boundary[1][0]:
                        self.x_start, self.y_start, self.x_end, self.y_end = self.outer_boundary[1][0], self.outer_boundary[0][1], self.outer_boundary[1][0], self.outer_boundary[1][1]
                    elif y < self.outer_boundary[0][0]:
                        self.x_start, self.y_start, self.x_end, self.y_end = self.outer_boundary[0][0], self.outer_boundary[0][1], self.outer_boundary[0][0], self.outer_boundary[1][1]
                    else:
                        self.x_start, self.y_start, self.x_end, self.y_end = midpoint, self.outer_boundary[0][1], midpoint, self.outer_boundary[1][1]
                # else:
                #     self.x_start, self.y_start, self.x_end, self.y_end = x, outer_boundary[0][1], x, outer_boundary[1][1]
        if event == cv2.EVENT_LBUTTONUP:
            # scan_radius = SCAN_RADIUS_COL_LINE
            # scan_region = self.im_thresh_bin[outer_boundary[0][1]:outer_boundary[1][1], x - scan_radius:x + scan_radius]
            self.column_line = [(self.x_start, self.y_start), (self.x_end, self.y_end)]
            self.drawing_column_line = False

    def setOuterBoundaryCoordiates(self, event, x, y, flags, param):
        self.x_cursor, self.y_cursor = x, y
        if event is cv2.EVENT_MOUSEMOVE and self.drawing_bboxes is False:
            self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = x - 31, y + 20, x - 5, y + 5
        if event == cv2.EVENT_LBUTTONDOWN and self.drawing_bboxes is False:
            self.x_start, self.y_start, self.x_end, self.y_end = x, y, x, y
            self.drawing_bboxes = True
            self.drawing_boundary = True
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing_bboxes is True:
            if self.drawing_boundary is True:
                self.x_end, self.y_end = x, y
        elif event is cv2.EVENT_LBUTTONUP and self.drawing_bboxes is True:
            self.x_end, self.y_end = x, y
            if self.x_end > self.x_start and self.y_end > self.y_start:
                self.drawing_boundary = False
                self.outer_boundary = [(self.x_start, self.y_start), (self.x_end, self.y_end)]
            elif self.x_start > self.x_end and self.y_end > self.y_start:
                self.drawing_boundary = False
                self.outer_boundary = [(self.x_end, self.y_start), (self.x_start, self.y_end)]
            elif self.x_end > self.x_start and self.y_start > self.y_end:
                self.drawing_boundary = False
                self.outer_boundary = [(self.x_start, self.y_end), (self.x_end, self.y_start)]
            elif self.x_start > self.x_end and self.y_start > self.y_end:
                self.drawing_boundary = False
                self.outer_boundary = [(self.x_end, self.y_end), (self.x_start, self.y_start)]
            self.drawing_boundary = False

    def setBBOXCoordiates(self, event, x, y, flags, param):
        boundary = param[0]
        if self.drawing_bbox and self.drawing_bboxes:
            if len(self.bboxes) == 0:
                if y > boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
                elif y < boundary[0][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
                else:
                    self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], y
            else:
                if y > boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = list(self.bboxes.values())[-1][0][0], list(self.bboxes.values())[-1][1][1], list(self.bboxes.values())[-1][1][0], boundary[1][
                        1]
                elif y < list(self.bboxes.values())[-1][1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = list(self.bboxes.values())[-1][0][0], list(self.bboxes.values())[-1][1][1], list(self.bboxes.values())[-1][1][0], \
                                                                         list(self.bboxes.values())[-1][1][1]
                else:
                    self.x_start, self.y_start, self.x_end, self.y_end = list(self.bboxes.values())[-1][0][0], list(self.bboxes.values())[-1][1][1], list(self.bboxes.values())[-1][1][0], y
            self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = self.x_start - 28, self.y_start, self.x_start - 2, self.y_start + 20
            self.label_ready = True

        if event == cv2.EVENT_LBUTTONUP:
            self.drawing_bbox = False
            if self.y_end >= boundary[1][1]:
                self.drawing_bboxes = False
        if event == cv2.EVENT_RBUTTONDOWN:
            self.drawing_mask = True
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing_mask == True:
            self.mask_x_offset, self.mask_y_offset = x - self.x_start, y - self.y_start
        elif event == cv2.EVENT_RBUTTONUP and self.drawing_mask == True:
            self.drawing_mask = False

    def scanAndSetBBOXCoordiates(self, event, x, y, flags, param):
        if self.drawing_bbox and self.drawing_bboxes:
            scan_radius = self.ui.bbox_scan_radius_spinbox.value()
            if len(self.bboxes) == 0:
                if y > self.unprocessed_reg_boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                elif y < self.unprocessed_reg_boundary[0][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                else:
                    # self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], y
                    scan_region = self.im_thresh_bin[y - scan_radius:y + scan_radius, self.unprocessed_reg_boundary[0][0]:self.unprocessed_reg_boundary[1][0]]
                    offset = -scan_radius
                    reg_rows = {}
                    cont_rows = []
                    start = True
                    for i in range(len(scan_region)):
                        avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                        reg_rows[y + offset] = avg_pixel_val
                        offset += 1
                        if avg_pixel_val >= self.ui.scan_row_avg_color_threshold_spinbox.value():
                            if start == False:
                                row = [y + offset]
                                cont_rows.append(row)
                                start = True
                            else:
                                if len(cont_rows) > 0:
                                    cont_rows[-1].append(y + offset)
                        else:
                            start = False
                    idx = None
                    max_len = 0
                    for i in range(len(cont_rows)):
                        reg = cont_rows[i]
                        if (reg[-1] - reg[0]) > max_len:
                            max_len = reg[-1] - reg[0]
                            idx = i
                    if idx is not None:
                        if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                            midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                        else:
                            midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                        if midpoint > self.unprocessed_reg_boundary[1][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                        elif y < self.unprocessed_reg_boundary[0][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                        else:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], midpoint
                    else:
                        self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], y

            else:
                bb_x_start, bb_y_start, bb_x_end, bb_y_end = list(self.bboxes.values())[-1][0][0], list(self.bboxes.values())[-1][1][1], list(self.bboxes.values())[-1][1][0], \
                                                             list(self.bboxes.values())[-1][1][1]
                if y > self.unprocessed_reg_boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, self.unprocessed_reg_boundary[1][1]
                elif y < bb_y_start:
                    self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
                else:
                    # self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_end, bb_x_end, y
                    scan_region = self.im_thresh_bin[y - scan_radius:y + scan_radius, bb_x_start:bb_x_end]
                    offset = -scan_radius
                    reg_rows = {}
                    cont_rows = []
                    start = True
                    for i in range(len(scan_region)):
                        avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                        # reg_rows[y + offset] = avg_pixel_val
                        offset += 1
                        if avg_pixel_val >= self.ui.scan_row_avg_color_threshold_spinbox.value():
                            if start == False:
                                row = [y + offset]
                                cont_rows.append(row)
                                start = True
                            else:
                                if len(cont_rows) > 0:
                                    cont_rows[-1].append(y + offset)
                        else:
                            start = False
                    idx = None
                    max_len = 0
                    for i in range(len(cont_rows)):
                        reg = cont_rows[i]
                        if (reg[-1] - reg[0]) > max_len:
                            max_len = reg[-1] - reg[0]
                            idx = i
                    if idx is not None:
                        if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                            midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                        else:
                            midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                        if midpoint > self.unprocessed_reg_boundary[1][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, self.unprocessed_reg_boundary[1][1]
                        elif y < bb_y_start:
                            self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
                        else:
                            self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, midpoint
                    else:
                        self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, y

            self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = self.x_start - 28, self.y_start, self.x_start - 2, self.y_start + 20
            self.label_ready = True

        if event == cv2.EVENT_LBUTTONUP:
            self.drawing_bbox = False
            if self.y_end >= self.unprocessed_reg_boundary[1][1]:
                self.drawing_bboxes = False
        if event == cv2.EVENT_RBUTTONDOWN:
            self.drawing_mask = True
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing_mask == True:
            self.mask_x_offset, self.mask_y_offset = x - self.x_start, y - self.y_start
        elif event == cv2.EVENT_RBUTTONUP and self.drawing_mask == True:
            self.drawing_mask = False

    def SASGridOuterBoundary(self, event, x, y, flags, param):
        if self.drawing_grid_outer_boundary and self.drawing_bboxes:
            if len(self.bboxes) == 0:
                if y > self.unprocessed_reg_boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                elif y < self.unprocessed_reg_boundary[0][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                else:
                    scan_region = self.im_thresh_bin[y - 20:y + 20, self.unprocessed_reg_boundary[0][0]:self.unprocessed_reg_boundary[1][0]]
                    offset = -20
                    reg_rows = {}
                    cont_rows = []
                    start = True
                    for i in range(40):
                        avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                        reg_rows[y + offset] = avg_pixel_val
                        offset += 1
                        if avg_pixel_val == 255:
                            if start == False:
                                row = [y + offset]
                                cont_rows.append(row)
                                start = True
                            else:
                                if len(cont_rows) > 0:
                                    cont_rows[-1].append(y + offset)
                        else:
                            start = False
                    idx = None
                    max_len = 0
                    for i in range(len(cont_rows)):
                        reg = cont_rows[i]
                        if (reg[-1] - reg[0]) > max_len:
                            max_len = reg[-1] - reg[0]
                            idx = i
                    if idx is not None:
                        if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                            midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                        else:
                            midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                        if midpoint > self.unprocessed_reg_boundary[1][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[1][1]
                        elif y < self.unprocessed_reg_boundary[0][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.unprocessed_reg_boundary[0][1]
                        else:
                            self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], midpoint
                    else:
                        self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], y

            else:
                bb_x_start, bb_y_start, bb_x_end, bb_y_end = list(self.bboxes.values())[-1][0][0], list(self.bboxes.values())[-1][1][1], list(self.bboxes.values())[-1][1][0], \
                                                             list(self.bboxes.values())[-1][1][1]
                if y > self.unprocessed_reg_boundary[1][1]:
                    self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, self.unprocessed_reg_boundary[1][1]
                elif y < bb_y_start:
                    self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
                else:
                    scan_region = self.im_thresh_bin[y - 20:y + 20, bb_x_start:bb_x_end]
                    offset = -20
                    cont_rows = []
                    start = True
                    for i in range(40):
                        avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                        offset += 1
                        if avg_pixel_val == 255:
                            if start == False:
                                row = [y + offset]
                                cont_rows.append(row)
                                start = True
                            else:
                                if len(cont_rows) > 0:
                                    cont_rows[-1].append(y + offset)
                        else:
                            start = False
                    idx = None
                    max_len = 0
                    for i in range(len(cont_rows)):
                        reg = cont_rows[i]
                        if (reg[-1] - reg[0]) > max_len:
                            max_len = reg[-1] - reg[0]
                            idx = i
                    if idx is not None:
                        if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                            midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                        else:
                            midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                        if midpoint > self.unprocessed_reg_boundary[1][1]:
                            self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, self.unprocessed_reg_boundary[1][1]
                        elif y < bb_y_start:
                            self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
                        else:
                            self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, midpoint
                    else:
                        self.x_start, self.y_start, self.x_end, self.y_end = bb_x_start, bb_y_start, bb_x_end, y

        if event == cv2.EVENT_LBUTTONUP:
            self.drawing_grid_outer_boundary = False

    def SASGridColumnBBoxes(self, event, x, y, flags, param):
        boundary = self.grid_outer_boundary
        if self.drawing_one_gcb and self.drawing_grid_column_bboxes:
            if len(self.grid_col_bboxes) > 0:
                boundary = boundary.copy()
                boundary[0] = (self.grid_col_bboxes[-1][1][0], self.grid_col_bboxes[-1][0][1])
            if x > boundary[1][0]:
                self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
            elif x < boundary[0][0]:
                self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[0][0], boundary[0][1]
            else:
                if not self.ui.grid_scan_mode_spinbox.isChecked():
                    self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], x, boundary[1][1]
                else:
                    if len(self.grid_col_bboxes) == 0 and self.white_columns is None:
                        grid_region = self.im_thresh_bin[boundary[0][1]:boundary[1][1], boundary[0][0]:boundary[1][0]]
                        grid_region = np.transpose(grid_region)
                        self.white_columns = 0
                        for i in range(len(grid_region)):
                            avg_pixel_val = int(np.floor(np.mean(grid_region[i])))
                            if avg_pixel_val == 255:
                                self.white_columns += 1
                            else:
                                # print("white col: " + str(self.white_columns))
                                break
                    scan_radius = self.ui.grid_column_line_scan_radius_spinbox.value()
                    scan_region = self.im_thresh_bin[boundary[0][1]:boundary[1][1], x - scan_radius:x + scan_radius]
                    scan_region = np.transpose(scan_region)
                    offset = -scan_radius
                    reg_columns = {}
                    cont_columns = []
                    start = True
                    for i in range(len(scan_region)):
                        avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                        reg_columns[x + offset] = avg_pixel_val
                        offset += 1
                        if avg_pixel_val == 255:
                            if start == False:
                                column = [x + offset]
                                cont_columns.append(column)
                                start = True
                            else:
                                if len(cont_columns) > 0:
                                    cont_columns[-1].append(x + offset)
                        else:
                            start = False
                    idx = None
                    max_len = 0
                    for i in range(len(cont_columns)):
                        reg = cont_columns[i]
                        if (reg[-1] - reg[0]) > max_len:
                            max_len = reg[-1] - reg[0]
                            idx = i
                    if idx is not None:
                        endpoint = cont_columns[idx][-1] - self.white_columns  # + 8
                        if endpoint > boundary[1][0]:
                            self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
                        elif x < boundary[0][0]:
                            self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], boundary[0][0], boundary[1][1]
                        else:
                            self.x_start, self.y_start, self.x_end, self.y_end = boundary[0][0], boundary[0][1], endpoint, boundary[1][1]
        if event == cv2.EVENT_LBUTTONUP:
            self.drawing_one_gcb = False
            if self.x_end >= boundary[1][0]:
                self.drawing_grid_column_bboxes = False

        if event == cv2.EVENT_RBUTTONDOWN:
            self.drawing_mask = True
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing_mask == True:
            self.mask_x_offset = x - self.x_start
        elif event == cv2.EVENT_RBUTTONUP and self.drawing_mask == True:
            self.drawing_mask = False

    def generateCode(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

    def addAnnotation(self, code, shape, operation, index, grid=False, header=None, append_to_last_saved_image=False, column_pos=None):
        self.annotations[code] = {}
        self.annotations[code]["shape"] = shape
        self.annotations[code]["shape"] = shape
        self.annotations[code]["operation"] = operation
        self.annotations[code]["index"] = index
        self.annotations[code]["grid"] = grid
        self.annotations[code]["header"] = header
        self.annotations[code]["append_to_last_saved_image"] = append_to_last_saved_image
        self.annotations[code]["self.column_position"] = self.column_position

    def delayToInspect(self):
        x_0, y_0, x_1, y_1 = self.outer_boundary[0][0], self.outer_boundary[1][1], self.outer_boundary[0][0], self.outer_boundary[1][1]
        l_x_0, l_y_0, l_x_1, l_y_1 = x_0, y_0 + 2, x_1 + 35, y_1 + 22
        cv2.rectangle(self.image_w_bboxes, (l_x_0, l_y_0), (l_x_1, l_y_1), Config.NEON_GREEN, -1)
        cv2.putText(self.image_w_bboxes, "VERIFY", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, Config.BLACK, 1, cv2.LINE_AA)
        cv2.imshow("image", self.image_w_bboxes)
        cv2.waitKey(1)
        self.mouse_clicked = False
        cv2.setMouseCallback("image", self.waitForMouseClick, [])
        while not self.mouse_clicked:
            cv2.waitKey(1)
            if keyboard.is_pressed('esc'):
                while keyboard.is_pressed('esc'):
                    continue
                self.undoBBoxDrawing()
                self.image_finalized = self.image_w_outer_boundary.copy()
                return False
        return True

    def waitForMouseClick(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            self.mouse_clicked = True


    def undoBBoxDrawing(self):
        undo_code = list(self.annotations.keys())[-1]
        undo_annotation = self.annotations.pop(undo_code)
        self.bboxes.pop(list(self.bboxes.keys())[-1])
        if undo_code in self.masks.keys():
            self.masks.pop(undo_code)
        if undo_annotation["shape"] == Config.SHAPE_LINE:
            if len(self.annotations) > 0:
                undo_code = list(self.annotations.keys())[-1]
                undo_annotation = self.annotations.pop(undo_code)
                self.bboxes.pop(undo_code)
                if undo_code in self.masks.keys():
                    self.masks.pop(undo_code)
            if len(self.annotations) > 0 \
                    and self.annotations[list(self.annotations.keys())[-1]]["self.column_position"] != self.column_position \
                    and self.column_position in [Config.COLUMN_LEFT, Config.COLUMN_RIGHT]:
                return False
        if undo_annotation["operation"] in [Config.OP_SIMPLE, Config.OP_APP_TO_LAST, Config.OP_COMBINE_W_H]:
            if undo_annotation["grid"] is True:
                for key in reversed(list(self.annotations.keys())):
                    if self.annotations[key]["grid"] is True:
                        self.bboxes.pop(key)
                        if self.IMAGE_TYPE == "Exercises":
                            self.masks.pop(key)
                        self.index_number = self.annotations.pop(key)["index"]
                    else:
                        annotation = self.annotations.pop(list(self.annotations.keys())[-1])
                        self.index_number = annotation["index"]
                        self.bboxes.pop(list(self.bboxes.keys())[-1])
                        break
            else:
                self.index_number = undo_annotation["index"]
        elif undo_annotation["operation"] == Config.OP_SET_HEADER:
            self.header = []
        elif undo_annotation["operation"] == Config.OP_APP_TO_HEAD:
            self.header.pop(-1)
        if undo_annotation["operation"] in Config.STANDARD_OPs:
            self.annotate_mode = undo_annotation["operation"]
        self.image_finalized = self.image_w_outer_boundary.copy()
        for key, bbox in zip(self.bboxes.keys(), self.bboxes.values()):
            if self.annotations[key]["shape"] != Config.SHAPE_LINE:
                color = Config.BBOX_COLOR[self.annotations[key]["operation"]]
                cv2.rectangle(self.image_finalized, bbox[0], bbox[1], color, 2)
                if self.IMAGE_TYPE == "Exercises" and self.annotations[key]["operation"] in [Config.OP_SIMPLE, Config.OP_COMBINE_W_H]:
                    mask = self.masks[key]
                    if self.annotations[key]["grid"]:
                        mask_width = (mask[1][0] - mask[0][0])
                        im_region = self.image_finalized[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width]
                        white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                        masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                        self.image_finalized[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width] = masked_reg
                        cv2.rectangle(self.image_finalized, (bbox[0][0], mask[0][1]), (bbox[0][0] + mask_width, mask[1][1]), color, 1)
                    else:
                        im_region = self.image_finalized[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]]
                        white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                        masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                        self.image_finalized[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]] = masked_reg
                        cv2.rectangle(self.image_finalized, mask[0], mask[1], color, 1)
                x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
                self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = x_0 - 28, y_0, x_1 - 2, y_1 + 20
                cv2.rectangle(self.image_finalized, (self.label_x_start, self.label_y_start), (self.label_x_end, self.label_y_end), color, -1)
                if self.annotations[key]["operation"] in [Config.OP_SET_HEADER, Config.OP_APP_TO_HEAD]:
                    label_str = "HEAD"
                    font_size = 0.30
                else:
                    label_str = str(self.annotations[key]["index"]).zfill(3)
                    font_size = 0.40
                cv2.putText(self.image_finalized, label_str, (self.label_x_start + 2, self.label_y_start + 14), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("image", self.image_finalized)
        cv2.waitKey(1)
        if len(self.bboxes) > 0:
            self.unprocessed_reg_boundary = [(self.outer_boundary[0][0], list(self.bboxes.values())[-1][1][1]), self.outer_boundary[1]]
        else:
            self.unprocessed_reg_boundary = self.outer_boundary
        self.label_x_start, self.label_y_start, self.label_x_end, self.label_y_end = self.unprocessed_reg_boundary[0][0] - 28, self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[0][0] - 2, self.unprocessed_reg_boundary[0][1] + 20
        self.mask_reg_col_line = [(self.mask_reg_col_line[0][0], self.unprocessed_reg_boundary[0][1]), (self.mask_reg_col_line[1][0], self.mask_reg_col_line[1][1])]
        self.x_start, self.y_start, self.x_end, self.y_end = self.unprocessed_reg_boundary[0][0], self.unprocessed_reg_boundary[0][1], self.unprocessed_reg_boundary[1][0], self.y_end

    #######################################################################################################################################################################################################
    #######################################################################################################################################################################################################
    #######################################################################################################################################################################################################
    #######################################################################################################################################################################################################
    #######################################################################################################################################################################################################
    #######################################################################################################################################################################################################
    #######################################################################################################################################################################################################
    def processImageWithBBoxes(self, current_set):
        for key, annotation in zip(self.annotations.keys(), self.annotations.values()):
            if annotation["shape"] != Config.SHAPE_LINE:
                if annotation["operation"] in [Config.OP_SIMPLE, Config.OP_COMBINE_W_H]:
                    if self.IMAGE_TYPE == "Exercises":
                        self.extractImageRegions(self.bboxes[key], self.masks[key], annotation, current_set)
                    else:
                        self.extractImageRegions(self.bboxes[key], None, annotation, current_set)
                elif annotation["operation"] == Config.OP_APP_TO_LAST:
                    self.extractImageRegions(self.bboxes[key], None, annotation, current_set)

    def extractImageRegions(self, bbox, mask, annotation, current_set):
        if annotation["operation"] == Config.OP_COMBINE_W_H and len(annotation["header"]) != 0:
            header_pngs = []
            for part_image in annotation["header"]:
                image_region = cv2.cvtColor(part_image, cv2.COLOR_BGRA2RGBA)
                buffer = io.BytesIO()
                Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                header_pngs.append(Image.open(buffer))
            width = max([bbox[1][0] - bbox[0][0]] + [header_png.size[0] for header_png in header_pngs])
            height = sum([bbox[1][1] - bbox[0][1]] + [header_png.size[1] for header_png in header_pngs])
            combined_image_regions = Image.new('RGBA', (width, height), (255, 255, 255))
            last_im_height = 0
            for header_png in header_pngs:
                combined_image_regions.paste(header_png, (0, last_im_height))
                last_im_height += header_png.size[1]
            if self.IMAGE_TYPE == "Exercises":
                masked_image = combined_image_regions.copy()
            image_region_temp = self.orig_image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
            image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
            buffer = io.BytesIO()
            Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
            png_image = Image.open(buffer)
            combined_image_regions.paste(png_image, (0, last_im_height))
            if self.IMAGE_TYPE == "Exercises":
                masked_region_temp = np.full((mask[1][1] - mask[0][1], mask[1][0] - mask[0][0], 4), 255, dtype=np.uint8)
                masked_region = cv2.cvtColor(masked_region_temp, cv2.COLOR_BGRA2RGBA)
                buffer_mask = io.BytesIO()
                Image.fromarray(masked_region, 'RGBA').save(buffer_mask, format='png')
                png_mask = Image.open(buffer_mask)
                masked_image.paste(png_image, (0, last_im_height))
                masked_image.paste(png_mask, (0, last_im_height))
        elif annotation["append_to_last_saved_image"]:
            if self.IMAGE_TYPE == "Exercises":
                # last_image_masked = self.setImageName(current_set, annotation["index"], "masked")
                # screenshot_top_masked = Image.open(os.path.join(Config.TEMP_SS_PATH, last_image_masked))
                screenshot_top_masked = self.extracted_image_arrays[annotation["index"]]["masked"]
                width = max([bbox[1][0] - bbox[0][0]] + [screenshot_top_masked.size[0]])
                height = sum([bbox[1][1] - bbox[0][1]] + [screenshot_top_masked.size[1]])
                masked_image = Image.new('RGBA', (width, height), (255, 255, 255))
                masked_image.paste(screenshot_top_masked, (0, 0))
                last_im_height = screenshot_top_masked.size[1]
                image_region_temp = self.orig_image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
                image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
                buffer = io.BytesIO()
                Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                png_image = Image.open(buffer)
                masked_image.paste(png_image, (0, last_im_height))
            # Unmasked
            # last_image_unmasked = self.setImageName(current_set, annotation["index"], "unmasked")
            # screenshot_top_unmasked = Image.open(os.path.join(Config.TEMP_SS_PATH, last_image_unmasked))
            if self.IMAGE_TYPE == "Exercises":
                screenshot_top_unmasked = self.extracted_image_arrays[annotation["index"]]["unmasked"]
            else:
                screenshot_top_unmasked = self.extracted_image_arrays[annotation["index"]]
            width = max([bbox[1][0] - bbox[0][0]] + [screenshot_top_unmasked.size[0]])
            height = sum([bbox[1][1] - bbox[0][1]] + [screenshot_top_unmasked.size[1]])
            combined_image_regions = Image.new('RGBA', (width, height), (255, 255, 255))
            combined_image_regions.paste(screenshot_top_unmasked, (0, 0))
            last_im_height = screenshot_top_unmasked.size[1]
            image_region_temp = self.orig_image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
            image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
            buffer = io.BytesIO()
            Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
            png_image = Image.open(buffer)
            combined_image_regions.paste(png_image, (0, last_im_height))
        else:
            width = bbox[1][0] - bbox[0][0]
            height = bbox[1][1] - bbox[0][1]
            combined_image_regions = Image.new('RGBA', (width, height), (255, 255, 255))
            image_region_temp = self.orig_image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
            image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
            buffer_image = io.BytesIO()
            Image.fromarray(image_region, 'RGBA').save(buffer_image, format='png')
            png_image = Image.open(buffer_image)
            combined_image_regions.paste(png_image, (0, 0))
            if self.IMAGE_TYPE == "Exercises":
                masked_region_temp = np.full((mask[1][1] - mask[0][1], mask[1][0] - mask[0][0], 4), 255, dtype=np.uint8)
                masked_region = cv2.cvtColor(masked_region_temp, cv2.COLOR_BGRA2RGBA)
                buffer_mask = io.BytesIO()
                Image.fromarray(masked_region, 'RGBA').save(buffer_mask, format='png')
                png_mask = Image.open(buffer_mask)
                masked_image = Image.new('RGBA', (width, height), (255, 255, 255))
                masked_image.paste(png_image, (0, 0))
                masked_image.paste(png_mask, (0, 0))
        if self.IMAGE_TYPE == "Exercises":
            self.extracted_image_arrays[annotation["index"]] = {
                "masked": masked_image.copy(),
                "unmasked": combined_image_regions.copy(),
            }
        elif self.IMAGE_TYPE == "Solutions":
            self.extracted_image_arrays[annotation["index"]] = combined_image_regions.copy()
        print("Screenshot processed: " + str(annotation["index"]))
        print("------------------------------------------")

