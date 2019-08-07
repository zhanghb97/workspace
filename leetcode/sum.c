
/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* twoSum(int* nums, int numsSize, int target, int* returnSize){
  for (int i = 0; i < numsSize; i++) {
    for (int j = 1; j < (numSize - i - 1); j++) {
      int result = *(nums + i) + *(nums + j);
      if (result == target) {
        // Return
      }
    }
  }
}
